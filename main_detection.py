import streamlit as st
import torch
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Create two columns
col1, col2 = st.columns([1, 2])

# Function to load and predict image
def predict_single_image(image_path, model_path, class_names):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load the model
    model = models.efficientnet_b2(pretrained=False)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()

    # Prepare the image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)

    # Make prediction
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]

    # Get predicted class and all probabilities
    predicted_class = class_names[predicted.item()]
    probabilities = probabilities.cpu().numpy()

    return predicted_class, probabilities

# Define the Streamlit app
def main():
    # Column 1: Logo
    with col1:
        logo = 'keeza.png'  # Replace with the path to your logo file
        st.image(logo, width=200)  # Adjust width as needed
    with col2:
        ds_img = 'desease_photo.png'  # Replace with the path to your logo file
        st.image(ds_img)  # Adjust width as needed
    # Column 2: Title and Description
    st.warning("Ocular Disease Detection")
    st.warning("Cataract | Diabetic Retinopathy | Glaucoma | Normal")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...",  type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)

        # Make prediction on the uploaded image
        model_path = 'eye_desease_data_4_classes.pth'  # Path to your model
        class_names = ['cataract', 'diabetic_retinopathy', 'glaucoma', 'normal']

        predicted_class, probabilities = predict_single_image(uploaded_file, model_path, class_names)
        st.markdown(f'Detected disease: {predicted_class}')

        # Save result to CSV
        save_prediction_to_csv(uploaded_file.name, predicted_class)

        # Plot probabilities as horizontal bar chart with percentage labels
        fig, ax = plt.subplots()
        colors = ['red', 'green', 'orange', 'blue']
        bars = ax.barh(class_names, probabilities, color=colors)

        for bar, prob in zip(bars, probabilities):
            ax.text(bar.get_width() - 0.05, bar.get_y() + bar.get_height(), 
                    f'{prob * 100:.1f}%', va='center', ha='right', 
                    color='black', fontsize=14, fontweight='bold')  # Increased fontsize

        ax.set_xlabel('Probability')
        ax.set_title('Probabilities')
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=12)  
        ax.set_xlim(0, 1.0)
        ax.grid(True)  # Add grid
        st.pyplot(fig, dpi=300)  # Increase DPI for clarity

        # Provide an option to download the CSV file
        csv_file = 'predictions.csv'
        if os.path.exists(csv_file):
            with open(csv_file, mode='r') as file:
                st.download_button(
                    label="Download Prediction Results",
                    data=file,
                    file_name=csv_file,
                    mime="text/csv"
                )

    st.markdown("<small style='color: lightblue;'><hr></small>", unsafe_allow_html=True)
    st.markdown("<small style='color: black;'>KeezaTech | +250788384528,+250788317992,+250785540835 | info@keezatech.rw |Noorsken - Kigali - Rwanda</small>", unsafe_allow_html=True)

    st.markdown(
        """
        <script>
        setInterval(function() {
            fetch('/stream');
        }, 60000);  // Ping the server every minute
        </script>
        """,
        unsafe_allow_html=True
    )

# Function to save predictions to CSV
def save_prediction_to_csv(image_name, predicted_class):
    csv_file = 'predictions.csv'
    
    # Check if the file already exists
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # If the file doesn't exist, write header
        if not file_exists:
            writer.writerow(['Image Name', 'Detected Disease'])
        
        # Write the prediction
        writer.writerow([image_name, predicted_class])

# Run the app
if __name__ == '__main__':
    main()
