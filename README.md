
# Krita - Automatic Sketch Colorization Plugin

This Krita plugin allows for automatic colorization of sketches on the canvas by utilizing an AI model trained to colorize line art with reference images. Perfect for users seeking to add vibrant colors to their line drawings, especially in an anime style.

## Key Features

- Automatically colorizes sketches using a reference image.
- Supports anime-style illustrations.
- Utilizes the **Anime-Sketch-Colorizer** model for enhanced color accuracy.
- Leverages neural networks for realistic colorization.

## Requirements

Ensure that you have the following Python packages installed for the plugin to work correctly:

- `torch`
- `torchvision`
- `numpy`
- `opencv-python`
- `opencv-transforms`
- `pillow`

### Installing the Packages

To install the required packages, run the following command in your terminal or command prompt:

```bash
pip install torch torchvision numpy opencv-python opencv-transforms pillow
```

## Downloading the Models

This plugin requires specific models to function. Download the models from the given repository or at https://drive.google.com/open?id=1pIZCjubtyOUr7AXtGQMvzcbKczJ9CtQG and save them in the appropriate directories:

- Place models for **color-to-sketch conversion** in `checkpoints/color2sketch`.
- Place models for **sketch-to-color conversion** in `checkpoints/sketch2color`.

Make sure the model files are in `.ckpt` format.

## Plugin Installation

1. **Download** and **extract** the plugin folder.
2. **Copy** all files from the `plugin` folder.
3. **Paste** them into Krita’s plugin directory:
   - On **Windows**: `C:\Users\[YourUserName]\AppData\Roaming\krita\pykrita`
   - On **Linux**: `~/.local/share/krita/pykrita`

## Usage

1. Open Krita.
2. Go to **Settings** > **Manage Plugins** and enable **Auto Sketch Colorization Plugin**.
3. Restart Krita if necessary.
4. Once activated, the plugin will allow you to colorize your sketches using reference images directly on the canvas.


Contributions to enhance this plugin are welcome! Feel free to submit issues or pull requests on the GitHub repository.

