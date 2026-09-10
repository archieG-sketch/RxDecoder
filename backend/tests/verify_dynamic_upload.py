import io
import httpx
from PIL import Image, ImageDraw

def test_dynamic_uploads():
    # 1. Ciprofloxacin test image
    img1 = Image.new('RGB', (650, 250), color=(255, 255, 255))
    d1 = ImageDraw.Draw(img1)
    d1.text((30, 20), 'St. Jude Urgent Care - Dr. Rebecca Taylor, MD', fill=(0, 0, 0))
    d1.text((30, 50), 'Patient: David Wilson, DOB: 08/19/1985', fill=(0, 0, 0))
    d1.text((30, 100), 'Rx: Ciprofloxacin 500mg tab', fill=(0, 0, 0))
    d1.text((30, 140), 'Sig: 1 tab PO BID with water x 10d', fill=(0, 0, 0))
    buf1 = io.BytesIO()
    img1.save(buf1, format='JPEG')

    # 2. Azithromycin test image
    img2 = Image.new('RGB', (650, 250), color=(255, 255, 255))
    d2 = ImageDraw.Draw(img2)
    d2.text((30, 20), 'Eastside Health - Dr. Kevin Zhao, MD', fill=(0, 0, 0))
    d2.text((30, 50), 'Patient: Maria Garcia, DOB: 11/04/1992', fill=(0, 0, 0))
    d2.text((30, 100), 'Rx: Azithromycin 250mg tab', fill=(0, 0, 0))
    d2.text((30, 140), 'Sig: 1 tab PO QD with water x 5d', fill=(0, 0, 0))
    buf2 = io.BytesIO()
    img2.save(buf2, format='JPEG')

    print("=== Testing Upload 1: Ciprofloxacin 500mg ===")
    files1 = {'file': ('rx_cipro.jpg', buf1.getvalue(), 'image/jpeg')}
    r1 = httpx.post('http://localhost:8000/api/decode', files=files1, timeout=20.0)
    print("Response Status:", r1.status_code)
    data1 = r1.json()
    print("Extracted Meds:", [m['name'] for m in data1['medications']])
    print("Extracted Strengths:", [m['strength'] for m in data1['medications']])
    print("Extracted Frequencies:", [m['frequency'] for m in data1['medications']])
    print("Checklist Count:", len(data1['checklist']))
    print("Checklist Preview:", [f"{c['time_of_day']}: {c['medication_name']} ({c['instructions']})" for c in data1['checklist'][:3]])

    print("\n=== Testing Upload 2: Azithromycin 250mg ===")
    files2 = {'file': ('rx_azithro.jpg', buf2.getvalue(), 'image/jpeg')}
    r2 = httpx.post('http://localhost:8000/api/decode', files=files2, timeout=20.0)
    print("Response Status:", r2.status_code)
    data2 = r2.json()
    print("Extracted Meds:", [m['name'] for m in data2['medications']])
    print("Extracted Strengths:", [m['strength'] for m in data2['medications']])
    print("Extracted Frequencies:", [m['frequency'] for m in data2['medications']])
    print("Checklist Count:", len(data2['checklist']))
    print("Checklist Preview:", [f"{c['time_of_day']}: {c['medication_name']} ({c['instructions']})" for c in data2['checklist'][:3]])

if __name__ == '__main__':
    test_dynamic_uploads()
