# CureCode
**Medical Prescription OCR Web App**

## **📌 Overview**
This is a **web application** that allows users to **upload doctors' prescriptions** and automatically extracts the **medicines prescribed** and **diagnosed diseases** into a **structured table format**. The app utilizes **Google Vision API** for **text extraction** and **AI/ML models** for classifying the extracted text.

## **🛠 Tech Stack**
- **Frontend:** HTML, CSS, EJS (Embedded JavaScript)
- **Backend:** Node.js, Express.js
- **Database:** MongoDB
- **OCR Engine:** Google Vision API
- **AI/ML Models:** Custom models for text classification

## **🚀 Features**
✔ Upload scanned or handwritten doctor prescriptions 📄  
✔ Extract text from images using **Google Vision API** 🔍  
✔ Automatically categorize **medicines and diagnosed diseases** 💊🦠  
✔ Store and retrieve patient records in **MongoDB** 🗄️  
✔ User-friendly **web interface** for easy access 🖥️  

## **📌 API Endpoints**
| Method | Endpoint        | Description |
|--------|----------------|-------------|
| `POST` | `/upload`       | Upload prescription image |
| `GET`  | `/patients`     | Fetch all patient records |
| `GET`  | `/patients/:id` | Fetch a single patient's details |

## **🤝 Contributions**
Feel free to **fork, raise issues, or submit PRs** to enhance this project! 🚀  

## **📜 License**
This project is licensed under the **MIT License**. 📝

