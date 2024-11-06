import torch
import os
import sys
import torchvision.transforms as transforms
import torchvision.utils as vutils

from .mymodels import Color2Sketch, Sketch2Color
from .dataloader import GetImageFolder

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


def load_model(device, nbclusters=9):
    with torch.no_grad():
        
        nbclusters = 9
        netC2S = Color2Sketch(pretrained=True).to(device)
    
        nc = 3 * (nbclusters + 1)
        netG = Sketch2Color(nc=nc, pretrained=True).to(device)

    return netG, netC2S


def process_images(edge_img, color_img, netG, netC2S, ncluster, device):

    test_transforms = transforms.Compose([
        transforms.Resize((512, 512))
    ])
    test_imagefolder = GetImageFolder(edge_img, test_transforms, netC2S, ncluster)
    test_loader = torch.utils.data.DataLoader(test_imagefolder, batch_size=1, shuffle=False)
    test_batch = next(iter(test_loader))

    refer_transforms = transforms.Compose([
        transforms.Resize((512, 512))
    ])
    refer_imagefolder = GetImageFolder(color_img, refer_transforms, netC2S, ncluster)
    refer_loader = torch.utils.data.DataLoader(refer_imagefolder, batch_size=1, shuffle=False)
    refer_batch = next(iter(refer_loader))

    infer_images(test_batch, refer_batch, netG, device)


def infer_images(test_batch, refer_batch, netG, device):
    with torch.no_grad():
        edge = test_batch[0].to(device)
        reference = refer_batch[1].to(device)
        color_palette = refer_batch[2]
        input_tensor = torch.cat([edge.cpu()]+color_palette, dim=1).to(device)
        fake = netG(input_tensor)
        
        # Créer une grille pour la sauvegarde
        result = torch.cat((reference, edge, fake), dim=-1).cpu()
        
        # Assurer que le répertoire de sortie existe
        save_path = os.path.join(FILE_PATH, "outputs")
        os.makedirs(save_path, exist_ok=True)
        
        # Sauvegarder la grille complète
        grid_output_file = os.path.join(save_path, "full_grid.png")
        vutils.save_image(result, grid_output_file, nrow=1, padding=5, normalize=True)


        
        # Sauvegarder uniquement l'image "fake"
        fake_output_file = os.path.join(save_path, "fake_output.png")
        vutils.save_image(fake, fake_output_file, normalize=True)


def main():
    if len(sys.argv) != 3:
        print("Usage: python test.py <path_to_color_image> <path_to_edge_image>")
        sys.exit(1)

    color_path = sys.argv[1]
    edge_path = sys.argv[2]

    if not os.path.exists(edge_path) or not os.path.exists(color_path):
        print("Error: Image file not found.")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Charger les modèles
    netG, netC2S = load_model(device)

    # Traiter les images
    process_images(edge_path, color_path, netG, netC2S, ncluster=9, device=device)



if __name__ == "__main__":
    main()


def generate():

    

    print(FILE_PATH)

    color_path = os.path.join(FILE_PATH, 'data', 'ref')
    edge_path = os.path.join(FILE_PATH, 'data', 'test')

    if not os.path.exists(edge_path) or not os.path.exists(color_path):
        print("Error: Image file not found.")
        sys.exit(1)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Charger les modèles
    netG, netC2S = load_model(device)

    # Traiter les images
    process_images(edge_path, color_path, netG, netC2S, ncluster=9, device=device)