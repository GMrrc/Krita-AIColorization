from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita

# installer les dépendances
from .install import install_requirements
install_requirements()

from .colorization import ColorizationDocker

DOCKER_ID = 'colorization'
instance = Krita.instance()


# Enregistrer le docker uniquement une fois
dock_widget_factory = DockWidgetFactory(
    DOCKER_ID,
    DockWidgetFactoryBase.DockRight,
    ColorizationDocker
)

instance.addDockWidgetFactory(dock_widget_factory)
