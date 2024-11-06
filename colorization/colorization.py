from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
import os
import shutil
from PIL import Image, ImageOps

from .sketch2Color.inference import generate

DOCKER_TITLE = 'colorization'

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
INF_PATH = os.path.join(FILE_PATH, 'sketch2Color','data','test', 'test')
REF_PATH = os.path.join(FILE_PATH, 'sketch2Color','data','ref', 'ref')
RESULT_PATH = os.path.join(FILE_PATH, 'sketch2Color','outputs')


class ColorizationDocker(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)

        main_widget = QWidget(self)
        self.setWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Boutons et widgets pour l'interface
        self.load_reference_button = QPushButton("Charger image de référence")
        self.load_reference_button.clicked.connect(self.load_reference_image)
        layout.addWidget(self.load_reference_button)

        self.run_inference_button = QPushButton("Lancer l'inférence")
        self.run_inference_button.clicked.connect(self.run_inference)
        layout.addWidget(self.run_inference_button)

        self.status_label = QLabel("Statut: En attente...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Variables pour gérer les images
        self.sketch_image_path = None
        self.colorized_image_path = None
        self.reference_image_path = None





    def save_sketch_image(self):
        """Sauvegarde une copie du sketch du canvas directement en tant qu'image PNG, avec un ratio 1:1 et des bordures blanches si nécessaire."""
        doc = Krita.instance().activeDocument()
        if doc:
            # Chemin de sauvegarde du fichier PNG
            self.sketch_image_path = os.path.join(INF_PATH, 'image_sketch.png')

            # Récupération de la taille du document
            width = doc.width()
            height = doc.height()

            # Extraction des pixels du canvas en tant que tableau numpy
            canvas_data = doc.pixelData(0, 0, width, height)
            np_image = np.frombuffer(canvas_data, dtype=np.uint8).reshape((height, width, 4))  # 4 canaux: RGBA

            # Création de l'image PIL à partir du tableau numpy
            image = Image.fromarray(np_image)

            # Ajustement du ratio 1:1 en ajoutant des bordures blanches
            if width != height:
                max_side = max(width, height)
                # Création d'une image carrée blanche
                square_image = Image.new('RGBA', (max_side, max_side), (255, 255, 255, 0))  # Fond transparent (ou blanc)
                # Centrage de l'image originale sur la nouvelle image carrée
                paste_x = (max_side - width) // 2
                paste_y = (max_side - height) // 2
                square_image.paste(image, (paste_x, paste_y))
            else:
                square_image = image

            # Sauvegarde de l'image finale en tant que PNG
            square_image.save(self.sketch_image_path, 'PNG')
        else:
            self.status_label.setText("Erreur : Aucun document actif trouvé.")



    def load_reference_image(self):
        """Permet à l'utilisateur de sélectionner une image de référence."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner l'image de référence", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_path:
            # Copier l'image dans le répertoire de travail
            self.reference_image_path = os.path.join(REF_PATH, 'image_color.png')
            shutil.copy(file_path, self.reference_image_path)
            self.status_label.setText(f"Image de référence sauvegardée")

    def run_inference(self):
        try:
            self.save_sketch_image()

            # Exécuter le modèle de colorisation
            self.status_label.setText("Lancement de l'inférence...")
            generate()

            self.colorized_image_path = os.path.join(RESULT_PATH, 'fake_output.png')

            # Afficher l'image colorisée dans un nouveau calque
            self.display_colorized_image_on_new_layer()

            self.status_label.setText("Inférence terminée")
        except Exception as e:
            self.status_label.setText(f"Erreur lors de l'inférence: {str(e)}")


    def display_colorized_image_on_new_layer(self):
        """Affiche l'image colorisée dans un nouveau calque et redimensionne selon le canvas avec un crop centré."""
        if not self.colorized_image_path:
            self.status_label.setText("Erreur: Aucune image colorisée disponible.")
            return

        image = QImage(self.colorized_image_path)
        doc = Krita.instance().activeDocument()

        if not doc:
            self.status_label.setText("Erreur: Aucun document actif.")
            return

        # Obtenir les dimensions du canvas
        canvas_width = doc.width()
        canvas_height = doc.height()

        # Charger l'image avec OpenCV pour pouvoir la redimensionner
        img_colorized_cv = cv2.imread(self.colorized_image_path)
        img_height, img_width, _ = img_colorized_cv.shape

        # Calculer les ratios de redimensionnement pour ajuster en fonction du canvas
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height

        # Choisir le plus grand facteur d'échelle pour couvrir le canvas
        scale_factor = max(scale_width, scale_height)

        # Calculer les nouvelles dimensions de l'image redimensionnée
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        # Redimensionner l'image avec l'interpolation bicubique
        resized_img = cv2.resize(img_colorized_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Recadrer l'image pour l'ajuster au centre du canvas
        # Calcul du décalage pour couper au centre
        x_offset = (new_width - canvas_width) // 2 if new_width > canvas_width else 0
        y_offset = (new_height - canvas_height) // 2 if new_height > canvas_height else 0

        # Cropper l'image au centre
        cropped_img = resized_img[y_offset:y_offset + canvas_height, x_offset:x_offset + canvas_width]

        # Sauvegarder l'image redimensionnée et recadrée temporairement
        resized_image_path = os.path.join(RESULT_PATH, 'resized_colorized_image.png')
        cv2.imwrite(resized_image_path, cropped_img)

        # Ajouter l'image redimensionnée dans un nouveau calque
        new_layer = doc.createNode("Colorized Layer", "paintlayer")
        doc.rootNode().addChildNode(new_layer, None)

        # Charger l'image recadrée dans le nouveau calque
        qimage_resized = QImage(resized_image_path)
        pixel_data = qimage_resized.bits().asstring(canvas_width * canvas_height * 4)
        new_layer.setPixelData(pixel_data, 0, 0, canvas_width, canvas_height)

        # Rafraîchir la vue du document
        doc.refreshProjection()


# Enregistrer le docker dans Krita
app = Krita.instance()
dock_widget_factory = DockWidgetFactory(
    DOCKER_TITLE,
    DockWidgetFactoryBase.DockRight,
    ColorizationDocker
)
app.addDockWidgetFactory(dock_widget_factory)
