from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from io import BytesIO
import torch
from torchvision import transforms
from animals_sber import animals_sber
from torchvision import models
import torch.nn as nn

class ResNet50Model(nn.Module):
    def __init__(self, num_classes):
        super(ResNet50Model, self).__init__()
        self.resnet = models.resnet50(weights=None)


        for param in self.resnet.parameters():
            param.requires_grad = False


        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.resnet(x)


app = FastAPI()


class_names = [
    'Alces (Лось)', 'Bison (зубр)', 'Canis lupus (Серый волк)',
    'Capreolus (косуля)', 'Cnippon (Пятнистый олень)', 'Lepus (Заяц)',
    'Lunx (Рысь)', 'Lutra (Выдра)', 'Martes (Куница)', 'Meles (Барсук)',
    'Neovison (Норка)', 'Nyctereutes (Енотовидная собака)', 'Putorius (Хорёк)',
    'Sus(Кабан)'
]


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


model = ResNet50Model(num_classes=len(class_names)).to(device)


try:
    model.load_state_dict(torch.load('best_resnet50.pth', map_location=device))
    model.eval()
except Exception as e:
    raise RuntimeError(f"Ошибка при загрузке весов: {e}")


transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(BytesIO(contents)).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs, 1)
            class_name = class_names[predicted.item()]
            translated = animals_sber.get(class_name, class_name)

        return {
            "original_class": class_name,
            "translated_class": translated
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "ok"}
