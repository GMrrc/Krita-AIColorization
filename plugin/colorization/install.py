import os
import subprocess
import sys

def install_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

    try:

        import torch
        import torchvision
        import cv2
        import opencv_transforms
        import numpy
        import PIL
        print("Toutes les dépendances sont déjà installées.")

    except ImportError:
        print("Installation des dépendances...")

        pip_command = [sys.executable, "-m", "pip", "install", "-r", requirements_file]

        try:
            subprocess.check_call(pip_command)
            print("Installation terminée.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation : {e}")
            
install_requirements()
