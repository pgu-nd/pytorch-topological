"""Example of classifying data using topological layers."""

from torch_topological.datasets import SphereVsTorus

from torch_topological.nn.data import make_tensor

from torch_topological.nn import VietorisRipsComplex
from torch_topological.nn.layers import StructureElementLayer

from torch.utils.data import DataLoader

import torch


class TopologicalModel(torch.nn.Module):
    def __init__(self, n_elements, latent_dim=64, output_dim=2):
        super().__init__()

        self.n_elements = n_elements
        self.latent_dim = latent_dim

        self.model = torch.nn.Sequential(
            StructureElementLayer(self.n_elements),
            torch.nn.Linear(self.n_elements, self.latent_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.latent_dim, output_dim),
        )

        self.vr = VietorisRipsComplex()

    def forward(self, x):
        pers_info = self.vr(x)
        pers_info = make_tensor(pers_info)

        return self.model(pers_info)


if __name__ == '__main__':

    batch_size = 32
    n_epochs = 10
    n_elements = 10

    data_set = SphereVsTorus(n_point_clouds=2 * batch_size)

    loader = DataLoader(
        data_set,
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
    )

    model = TopologicalModel(n_elements)
    loss_fn = torch.nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(n_epochs):
        for batch, (x, y) in enumerate(loader):
            pred = model(x)
            loss = loss_fn(pred, y)

            print(loss.item())

            opt.zero_grad()
            loss.backward()
            opt.step()
