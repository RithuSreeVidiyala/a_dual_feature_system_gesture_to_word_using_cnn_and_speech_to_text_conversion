<h2>A Dual-Feature System: Gesture-to-Word using CNN and Speech-to-Text Conversion</h2>  

## *Overview*  
This project provides an assistive communication system for the deaf and mute community. It features two modules:  
1️⃣ *Gesture-to-Word Recognition:* Uses a deep learning model to recognize American Sign Language (ASL) gestures from a webcam.  
2️⃣ *Speech-to-Text Conversion:* Uses Google Speech APIs to transcribe speech into text.  

This project aims to *provide a dual-feature system* by enabling interaction between deaf, mute, and non-sign language users.  

## *Key Features*  
✅ *Real-Time Gesture Recognition:* Identifies ASL hand signs via webcam and converts them into words.  
✅ *Speech-to-Text Transcription:* Converts spoken language into text for real-time communication.  
✅ *User-Friendly Interface:* A simple UI for ease of interaction.  
✅ *Multimodal Communication:* Enables conversations between a deaf and a mute person.  

## *Technology Stack*  
- *Backend:* Python 3.10.14 
- *Deep Learning Model:* CNN (Convolutional Neural Network) with MobileNet  
- *Speech Processing:* Google Web Speech API + SpeechRecognition  
- *Libraries:* OpenCV, TensorFlow, Keras, PyTorch, NumPy  

## *How to Run the Project*  

### *1️⃣ Set Up a Virtual Environment*  
cmd
python -m venv myenv


### *2️⃣ Activate Virtual Environment*  
 
cmd
conda activate myenv

### *3️⃣ Install Dependencies*  
cmd
pip install -r requirements.txt


### *4️⃣ Run the Application*  
cmd
python app.py


### *5️⃣ Access the Web App*  
Open your browser and visit:  
bash
http://127.0.0.1:5000/


