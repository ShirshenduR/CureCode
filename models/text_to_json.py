import re
import json
import requests
from typing import Dict, List, Any, Optional

class PrescriptionParser:

    def __init__(self, api_key: str, api_url: str = "https://openrouter.ai/api/v1/chat/completions",
                 site_url: str = None, site_name: str = None):
      
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        if site_url:
            self.headers["HTTP-Referer"] = site_url
        if site_name:
            self.headers["X-Title"] = site_name

    def extract_information(self, prescription_text: str) -> Dict[str, Any]:
        # First use regex for initial extraction
        initial_data = self._regex_extraction(prescription_text)

        # Then use DeepSeek via OpenRouter to finalize, deduplicate and format the JSON
        final_data = self._deepseek_formatting(prescription_text, initial_data)

        return final_data

    def _regex_extraction(self, text: str) -> Dict[str, Any]:
        data = {
            "Patient Name": None,
            "Age": None,
            "Gender": None,
            "UHID": None,
            "Doctor Name": None,
            "Diagnosis": None,
            "Prescription": [],
            "Advice": []
        }

        # Extract patient information
        patient_pattern = r"([A-Za-z\s]+)\s*\((\d+)/([MF])\)"
        patient_match = re.search(patient_pattern, text)
        if patient_match:
            data["Patient Name"] = patient_match.group(1).strip()
            data["Age"] = int(patient_match.group(2))
            data["Gender"] = patient_match.group(3)

        # Extract UHID
        uhid_pattern = r"UHID:\s*([A-Za-z0-9\-]+)"
        uhid_match = re.search(uhid_pattern, text)
        if uhid_match:
            data["UHID"] = uhid_match.group(1)
        else:
            # Try alternative pattern for Patient ID
            uhid_pattern = r"Patient ID:?\s*([A-Za-z0-9\-]+)"
            uhid_match = re.search(uhid_pattern, text)
            if uhid_match:
                data["UHID"] = uhid_match.group(1).strip()

        # Extract doctor name
        doctor_pattern = r"Doctor:?\s*([Dr|Dr.]+\s+[A-Za-z\s]+)\s*\("
        doctor_match = re.search(doctor_pattern, text)
        if doctor_match:
            data["Doctor Name"] = doctor_match.group(1).strip()
        else:
            # Alternative patterns
            alt_patterns = [
                r"Consulting Doctor:?\s*([Dr|Dr.]+\s+[A-Za-z\s]+)",
                r"Attending Physician:?\s*([Dr|Dr.]+\s+[A-Za-z\s]+)",
                r"Physician:?\s*([Dr|Dr.]+\s+[A-Za-z\s]+)"
            ]

            for pattern in alt_patterns:
                doctor_match = re.search(pattern, text)
                if doctor_match:
                    data["Doctor Name"] = doctor_match.group(1).strip()
                    break

        # Extract diagnosis
        diagnosis_patterns = [
            r"Diagnosis:?\s*([^\n]+)",
            r"Assessment:?\s*([^\n]+)"
        ]

        for pattern in diagnosis_patterns:
            diagnosis_match = re.search(pattern, text)
            if diagnosis_match:
                data["Diagnosis"] = diagnosis_match.group(1).strip()
                break

        # Extract prescription items (medications and treatments)
        # Check for different section headings
        prescription_section = ""
        prescription_headers = ["Prescription:", "Medications:"]
        advice_headers = ["Advice:", "Guidance:", "Instructions:"]

        for header in prescription_headers:
            if header in text:
                split_text = text.split(header)[1]
                for advice_header in advice_headers:
                    if advice_header in split_text:
                        prescription_section = split_text.split(advice_header)[0]
                        break
                else:
                    prescription_section = split_text.split("Doctor's Signature:")[0] if "Doctor's Signature:" in split_text else split_text.split("Doctor's Endorsement:")[0] if "Doctor's Endorsement:" in split_text else split_text
                break

        if not prescription_section:
            prescription_section = text

        if prescription_section:

            med_patterns = [
                r"(Tab\.\s+[\w\s\d\.\-\(\)]+\s+–\s+[^\n]+)",
                r"(Syp\.\s+[\w\s\d\.\-\(\)]+\s+–\s+[^\n]+)",
                r"(Cap\.\s+[\w\s\d\.\-\(\)]+\s+–\s+[^\n]+)",
                r"(Inj\.\s+[\w\s\d\.\-\(\)]+\s+–\s+[^\n]+)",
                r"([\w\s]+\s+inhalation\s+–\s+[^\n]+)",
                r"([\w\s]+\s+gargles\s+–\s+[^\n]+)",
                r"(Tab\.\s+[\w\s\d\.\-\(\)]+\s*[0-9]+\s*mg\s*–[^\n]+)",
                r"(Tab\.\s+[\w\s\d\.\-\(\)]+\s*[0-9]+\s*mg[^\n]+)"
            ]

            for pattern in med_patterns:
                matches = re.findall(pattern, prescription_section)
                for match in matches:
                    data["Prescription"].append(match.strip())

       
        advice_section = ""
        for advice_header in advice_headers:
            if advice_header in text:
                advice_section = text.split(advice_header)[1]
                if "Doctor's Signature:" in advice_section:
                    advice_section = advice_section.split("Doctor's Signature:")[0]
                elif "Doctor's Endorsement:" in advice_section:
                    advice_section = advice_section.split("Doctor's Endorsement:")[0]
                elif "Next Review:" in advice_section:
                    advice_section = advice_section.split("Next Review:")[0]
                break

        if advice_section:
            
            advice_items = re.split(r'[.\n]+', advice_section)
            for item in advice_items:
                item = item.strip()
                if item and len(item) > 5:  
                    data["Advice"].append(item + ".")

        return data

    def _deepseek_formatting(self, text: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare the prompt for DeepSeek
        system_prompt = """
        You are an expert medical information extractor with meticulous attention to detail. Your task is to extract
        and format prescription information into a specific JSON structure.

        The output must strictly follow this JSON format:
        {
            "Patient Name": "string",
            "Age": number,
            "Gender": "string",
            "UHID": "string",
            "Doctor Name": "string",
            "Diagnosis": "string",
            "Prescription": [
                "string item 1",
                "string item 2",
                ...
            ],
            "Advice": [
                "string advice 1",
                "string advice 2",
                ...
            ]
        }

        Critical requirements:
        0.The information may use different category names
        than those in the JSON format, but you are able to identify these and accurately place the information.
        1. Remove any duplicate entries in the Prescription and Advice arrays
        2. Ensure Age is a number, not a string
        3. Make sure entries in arrays are complete and properly formatted
        4. Follow the exact JSON structure provided
        5. Provide only the JSON output with no additional text
        6. Make sure none of the json categories overlap
        7. If any category is null, try to create it yourself from the data
        """

        user_prompt = f"""
        Here is the raw prescription text:

        {text}

        I've already extracted some information using regex:
        {json.dumps(initial_data, indent=2)}

        Please format this into the required JSON structure, filling in any missing information
        from the raw text. Make sure to remove any duplicate entries in the arrays.

        The final output should follow exactly this format:

        ```json
        {{
            "Patient Name": "Ramesh Verma",
            "Age": 38,
            "Gender": "M",
            "UHID": "CL-20250312-003",
            "Doctor Name": "Dr. Amit Mehta",
            "Diagnosis": "Acute Upper Respiratory Tract Infection (URTI) with mild fever",
            "Prescription": [
                "Tab. Paracetamol 500 mg – 1 tab TDS × 3 days (For fever and body pain)",
                "Tab. Levocetirizine 5 mg – 1 tab OD × 5 days (For cold & allergy)",
                "Syp. Grilinctus 5 ml – TDS × 5 days (For cough)",
                "Tab. Pantoprazole 40 mg – 1 tab OD before breakfast × 5 days (For gastric protection)",
                "Steam inhalation – 2 times daily",
                "Warm saline gargles – 3 times daily"
            ],
            "Advice": [
                "Drink plenty of fluids and rest adequately.",
                "Avoid cold drinks and oily/spicy food.",
                "Follow-up if symptoms persist beyond 5 days."
            ]
        }}
        ```

        Return only the JSON output with no other text. Ensure there are no duplicates in the arrays, and make sure the output is valid, perfectly formatted JSON.
        """

        # Openrouter call to deepseek
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3  # Low -> dteterministic results
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()

       
            result = response.json()
            model_response = result["choices"][0]["message"]["content"]

          
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            json_match = re.search(json_pattern, model_response)

            if json_match:
                json_str = json_match.group(1)
            else:
            
                json_start = model_response.find('{')
                json_end = model_response.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = model_response[json_start:json_end]
                else:
                    print("Could not extract JSON from model response")
                    # If we can't extract JSON, perform deduplication manually
                    return self._manually_deduplicate(initial_data)

            try:
                final_data = json.loads(json_str)

                # Double-check deduplication
                return self._manually_deduplicate(final_data)

            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                # If JSON parsing fails, perform deduplication manually
                return self._manually_deduplicate(initial_data)

        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            # If API call fails, perform deduplication manually
            return self._manually_deduplicate(initial_data)

    def _manually_deduplicate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = data.copy()

       
        if "Age" in result and result["Age"] is not None:
            if isinstance(result["Age"], str):
                try:
                    result["Age"] = int(result["Age"])
                except ValueError:
                    pass

        if "Prescription" in result and isinstance(result["Prescription"], list):
            result["Prescription"] = list(dict.fromkeys(result["Prescription"]))

  
        if "Advice" in result and isinstance(result["Advice"], list):
            result["Advice"] = list(dict.fromkeys(result["Advice"]))

        return result

    def format_output(self, structured_data: Dict[str, Any]) -> str:
        """
        Format the structured data as a perfectly formatted JSON string.

        Args:
            structured_data: The structured prescription information

        Returns:
            A JSON string representation of the data
        """
        return json.dumps(structured_data, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Sample prescription text
    sample_prescription = "Patient Name: Priya Reddy (35/F) UHID: CL-20250315-012 Date: 15/03/25 Doctor: Dr. Ananya Das, MBBS, MD (Gynecology) Clinic: Sunshine Women’s Clinic, Pune Diagnosis: PCOS with irregular periods Prescription: Metformin 500mg – 1 tab BD × 3 months OCP (Diane-35) – 1 tab OD × 21 days, repeat as advised Vitamin D3 60K – 1 cap weekly × 8 weeks Low GI diet, daily 30-min exercise Advice: Maintain a healthy weight, reduce sugar intake Manage stress, track periods Follow-up: After 2 months for hormonal assessment Doctor’s Signature: Dr. Ananya Das (Reg. No: XXXXX)"

    # Initialize the parser with your API key
    parser = PrescriptionParser(
        api_key="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", #<-api key (needs to be hidden)
        site_url=".", 
        site_name="."  
    )

    # Extract information
    structured_info = parser.extract_information(sample_prescription)

    # Format and print the output
    json_output = parser.format_output(structured_info)
    print(json_output)
