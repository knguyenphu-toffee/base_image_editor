import os
import base64
import mimetypes
import random
import time
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseImageEditor:
    def __init__(self, api_key):
        """
        Initialize the Base Image Editor with Google Gemini API
        
        Args:
            api_key (str): Your Google AI API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash-image-preview"
        
        # Define paths
        self.starting_image_dir = "starting_image"
        self.output_dir = "output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_base_image_path(self):
        """
        Find the base image in the starting_image directory
        
        Returns:
            str: Path to the base image file
        """
        if not os.path.exists(self.starting_image_dir):
            raise FileNotFoundError(f"Starting image directory '{self.starting_image_dir}' not found")
        
        # Get all image files in the directory
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
        image_files = []
        
        for file in os.listdir(self.starting_image_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(file)
        
        if not image_files:
            raise FileNotFoundError("No image files found in starting_image directory")
        
        if len(image_files) > 1:
            print(f"Multiple images found, using: {image_files[0]}")
        
        return os.path.join(self.starting_image_dir, image_files[0])
    
    def load_image_as_base64(self, image_path):
        """
        Load image file and convert to base64
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (base64_data, mime_type)
        """
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            # Default to PNG if can't determine
            mime_type = "image/png"
            
        return image_base64, mime_type
    
    def generate_random_outfit_prompt(self):
        """
        Generate a random casual outfit description
        
        Returns:
            str: Description of a casual outfit
        """
        tops = [
            "plain t-shirt", "hoodie", "sweater", "cardigan", "blouse", "tank top",
            "long-sleeve shirt", "polo shirt", "button-up shirt", "crop top",
            "plain t-shirt", "graphic tee", "hoodie", "crewneck sweater", "zip-up hoodie",
            "cardigan", "blouse", "tank top", "long-sleeve shirt", "crop top",
            "off-shoulder top", "button-up shirt", "polo shirt", "tube top", "knit top",
            "halter top", "peplum top", "wrap top", "mock neck top", "camisole"
        ]
        
        bottoms = [
            "jeans", "leggings", "sweatpants", "shorts", "joggers", "chinos",
            "casual pants", "denim shorts", "yoga pants", "wide-leg trousers",
            "jeans", "denim shorts", "leggings", "joggers", "sweatpants",
            "cargo pants", "bike shorts", "mini skirt", "midi skirt",
            "culottes", "overalls", "capri pants", "khaki shorts", "skort",
            "paperbag waist shorts", "pleated skirt", "track pants", "flare jeans", 
            "athletic shorts"
        ]
        
        accessories = [
            "", "with a simple necklace", "with small earrings", "with a bracelet", ""
        ]

        top = random.choice(tops)
        bottom = random.choice(bottoms)
        accessory = random.choice(accessories)
        
        outfit = f"neutral colored {top} and {bottom} {accessory}".strip()
        return outfit
    
    def generate_background_variation(self):
        """
        Generate a description for bedroom background variation
        
        Returns:
            str: Description of bedroom background variation
        """
        bedroom_elements = [
            "slightly shift the camera angle to show more of the left side of the bedroom",
            "adjust the view to reveal more of the right side of the room",
            "shift the perspective to show a bit more of the background wall",
            "move the viewpoint to include more of the bedroom decor in the background",
            "adjust the angle to show a different section of the room's furniture",
            "shift the frame to reveal more of the bedroom's ambient lighting",
            "change the perspective to show a different corner of the bedroom",
            "modify the view to include more of the bedroom's wall decorations",
            "adjust the framing to show a slightly different portion of the room",
            "shift the camera position to reveal different bedroom elements in the background"
        ]
        
        return random.choice(bedroom_elements)
    
    def create_variation_prompt(self, variation_number, expression_type):
        """
        Create a detailed prompt for image variation
        
        Args:
            variation_number (int): The variation number
            expression_type (str): Type of expression change ('neutral' or 'sobbing')
            
        Returns:
            str: Complete prompt for image generation
        """
        outfit = self.generate_random_outfit_prompt()
        background_change = self.generate_background_variation()
        
        # Set expression change based on type
        if expression_type == 'neutral':
            expression_change = "\n4. EXPRESSION: alter her expression to a different neutral expression with a change in head tilt."
        elif expression_type == 'sobbing':
            expression_change = "\n4. EXPRESSION: Change her expression and make it look like she is sobbing."
        else:
            expression_change = ""
        
        prompt = f"""Create a variation of this selfie image with the following changes:

1. CLOTHING: Change the person's outfit to: {outfit}. Keep the style casual and natural-looking.

2. BACKGROUND: {background_change}. Maintain the same setting as the original input image with a slight perspective change.

3. REQUIREMENTS:
   - Keep the same person's face and general pose
   - If the person's arm is extended under the camera, keep it in a selfie position with arm etended below.
   - Maintain the selfie/portrait style composition
   - Keep lighting natural and consistent with a bedroom environment
   - Ensure the outfit looks realistic and well-fitted
   - Keep the overall mood and atmosphere similar to the original
   - Do not change any of the decor or bedroom background
   - Keep the person's position the same
   - Do not change the setting
   - No artifacts or filters on the image
   - No change in camera position{expression_change}

Generate a high-quality, realistic variation that maintains the original's authenticity while incorporating these changes."""

        return prompt
    
    def save_binary_file(self, file_name, data):
        """
        Save binary data to file
        
        Args:
            file_name (str): Name of the file to save
            data (bytes): Binary data to save
        """
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"✓ File saved to: {file_name}")
    
    def generate_variation(self, base_image_path, prompt, variation_number, expression_type):
        """
        Generate a single image variation using Gemini
        
        Args:
            base_image_path (str): Path to the base image
            prompt (str): Generation prompt
            variation_number (int): Variation number for naming
            expression_type (str): Type of expression for display
            
        Returns:
            bool: Success status
        """
        try:
            # Add indicator for expression type
            variation_type = f" (with {expression_type} expression)"
            print(f"Generating variation {variation_number}/5{variation_type}...")
            
            # Load image as base64
            image_base64, mime_type = self.load_image_as_base64(base_image_path)
            
            # Create contents for the API call
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type=mime_type,
                            data=base64.b64decode(image_base64),
                        ),
                        types.Part.from_text(text=prompt),
                    ],
                ),
                types.Content(
                    role="model",
                    parts=[],
                ),
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="Generate the variation now."),
                    ],
                ),
            ]
            
            # Configure generation
            generate_content_config = types.GenerateContentConfig(
                response_modalities=[
                    "IMAGE",
                    "TEXT",
                ],
            )
            
            # Generate content stream
            file_saved = False
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                # Check for image data
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):
                    
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    
                    if not file_extension:
                        file_extension = ".png"  # Default to PNG
                    
                    output_filename = f"{expression_type}_variation_{variation_number:02d}{file_extension}"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    self.save_binary_file(output_path, data_buffer)
                    file_saved = True
                    break
                
                # Print any text output
                elif hasattr(chunk, 'text') and chunk.text:
                    print(f"Response text: {chunk.text}")
            
            return file_saved
            
        except Exception as e:
            print(f"✗ Error generating variation {variation_number}: {str(e)}")
            return False
    
    def generate_variations(self, expression_type):
        """
        Generate 5 variations of the base image with specified expression type
        
        Args:
            expression_type (str): Type of expression ('neutral' or 'sobbing')
            
        Returns:
            int: Number of successfully generated variations
        """
        try:
            # Get the base image path
            base_image_path = self.get_base_image_path()
            print(f"Using base image: {base_image_path}")
            
            # Clear output directory of previous variations with same expression type
            for file in os.listdir(self.output_dir):
                if file.startswith(f"{expression_type}_") and file.endswith(('.png', '.jpg', '.jpeg')):
                    os.remove(os.path.join(self.output_dir, file))
            
            successful_generations = 0
            
            # Generate 5 variations
            for i in range(1, 6):
                prompt = self.create_variation_prompt(i, expression_type)
                
                if self.generate_variation(base_image_path, prompt, i, expression_type):
                    successful_generations += 1
                
                # Add a delay to avoid rate limiting
                print("Waiting 3 seconds before next generation...")
                time.sleep(3)
            
            print(f"\n🎉 Generation complete! {successful_generations}/5 {expression_type} variations created successfully.")
            print(f"📁 Output files saved in: {self.output_dir}/")
            
            return successful_generations
            
        except Exception as e:
            print(f"❌ Error during generation process: {str(e)}")
            return 0

    def display_menu(self):
        """
        Display the main menu options
        """
        print("\n" + "=" * 50)
        print("🎨 Image Variation Generator - Menu")
        print("=" * 50)
        print("1. Generate 5 neutral expression variations")
        print("2. Generate 5 sobbing expression variations") 
        print("3. Quit")
        print("=" * 50)

def main():
    """
    Main function to run the base image editor with menu system
    """
    print("🎨 Base Image Editor - Selfie Variation Generator")
    print("=" * 50)
    
    # Get API key from environment variable or user input
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
    
    if not api_key:
        print("⚠️  Gemini API key not found in environment variables.")
        print("Looking for GEMINI_API_KEY or GOOGLE_AI_API_KEY in .env file")
        api_key = input("Please enter your Gemini API key: ").strip()
        
        if not api_key:
            print("❌ API key is required to run this script.")
            return
    
    try:
        # Initialize the editor
        editor = BaseImageEditor(api_key)
        
        while True:
            editor.display_menu()
            choice = input("Enter your choice (1, 2, or 3): ").strip()
            
            if choice == "1":
                print("\n🎭 Generating neutral expression variations...")
                successful = editor.generate_variations("neutral")
                if successful > 0:
                    print(f"\n✨ Successfully created {successful} neutral expression variations!")
                else:
                    print("\n❌ No neutral variations were created successfully.")
                    
            elif choice == "2":
                print("\n😢 Generating sobbing expression variations...")
                successful = editor.generate_variations("sobbing")
                if successful > 0:
                    print(f"\n✨ Successfully created {successful} sobbing expression variations!")
                else:
                    print("\n❌ No sobbing variations were created successfully.")
                    
            elif choice == "3":
                print("\n👋 Thank you for using the Image Variation Generator!")
                print("🎬 Your variations are ready for AI video generation!")
                break
                
            else:
                print("\n❌ Invalid choice. Please enter 1, 2, or 3.")
            
            # Ask if user wants to continue after successful generation
            if choice in ["1", "2"]:
                continue_choice = input("\nWould you like to generate more variations? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("\n👋 Thank you for using the Image Variation Generator!")
                    print("🎬 Your variations are ready for AI video generation!")
                    break
            
    except Exception as e:
        print(f"❌ Script error: {str(e)}")

if __name__ == "__main__":
    main()
