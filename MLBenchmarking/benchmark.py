import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import time

# Device configuration


transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

batch_size = 32

trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

cfg = {
   'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
}

class VGG(nn.Module):
    def __init__(self, vgg_name):
        super(VGG, self).__init__()
        self.features = self._make_layers(cfg[vgg_name])
        self.classifier = nn.Linear(512, 10)

    def forward(self, x):
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for x in cfg:
            if x == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                layers += [nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                           nn.BatchNorm2d(x),
                           nn.ReLU(inplace=True)]
                in_channels = x
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)

# Benchmarking function
def benchmark_training(device, train_loader, num_epochs):
    device = torch.device(device)
    model = VGG('VGG11').to(device)
    model.train()
    total_time = 0
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    for epoch in range(num_epochs):
        start_time = time.time()
        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        end_time = time.time()
        epoch_time = end_time - start_time
        total_time += epoch_time
        print(f"Epoch [{epoch + 1}/{num_epochs}], Time Taken: {epoch_time:.2f} seconds")

    avg_time_per_epoch = total_time / num_epochs
    print(f"\nAverage Time per Epoch: {avg_time_per_epoch:.2f} seconds")
    print(f"\nTotal time: {total_time:.2f} seconds")
    return avg_time_per_epoch

# Run the benchmark

if __name__ == "__main__":
    #print("Benchmarking on GPU:")
    #benchmark_training("cuda", trainloader, 10)
    print("Benchmarking on CPU:")
    benchmark_training("cpu", trainloader, 2)
