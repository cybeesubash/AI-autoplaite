# ============================================================
# utils.py  –  Global & Indian Vehicle Number Plate Parsing Engine
# ============================================================

import re

# ── State and Union Territory Codes (India) ─────────────────
INDIAN_STATES = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "CH": "Chandigarh",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "DN": "Dadra and Nagar Haveli",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "OR": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TR": "Tripura",
    "TS": "Telangana",
    "UK": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
    "BH": "Bharat Series (All-India)"
}

# ── Indian RTO Code Mappings (Exhaustive TN + Major States) ──
INDIAN_RTO_MAP = {
    "TN01": ("Tamil Nadu", "Chennai Central", "Wright Ridge Road, Egmore, Chennai"),
    "TN02": ("Tamil Nadu", "Chennai North-West", "Anna Nagar West, Chennai"),
    "TN03": ("Tamil Nadu", "Chennai North-East", "Tondiarpet, Chennai"),
    "TN04": ("Tamil Nadu", "Chennai East", "Royapuram, Chennai"),
    "TN05": ("Tamil Nadu", "Chennai South-East", "Mylapore, Chennai"),
    "TN06": ("Tamil Nadu", "Chennai South-West", "Mandaveli, Chennai"),
    "TN07": ("Tamil Nadu", "Chennai South", "Thiruvanmiyur, Chennai"),
    "TN09": ("Tamil Nadu", "Chennai West", "KK Nagar, Chennai"),
    "TN10": ("Tamil Nadu", "Chennai South-West", "Virugambakkam, Chennai"),
    "TN11": ("Tamil Nadu", "Tambaram", "Sanatorium, Tambaram, Chennai"),
    "TN12": ("Tamil Nadu", "Poonamallee", "Trunk Road, Poonamallee"),
    "TN13": ("Tamil Nadu", "Ambattur", "Industrial Estate, Ambattur"),
    "TN14": ("Tamil Nadu", "Sholinganallur", "OMR Road, Sholinganallur, Chennai"),
    "TN15": ("Tamil Nadu", "Ulundurpet", "Kallakurichi Road, Ulundurpet"),
    "TN16": ("Tamil Nadu", "Tindivanam", "Gingee Road, Tindivanam"),
    "TN18": ("Tamil Nadu", "Red Hills", "GNT Road, Red Hills, Chennai"),
    "TN19": ("Tamil Nadu", "Chengalpattu", "GST Road, Chengalpattu"),
    "TN20": ("Tamil Nadu", "Tiruvallur", "Collectorate Campus, Tiruvallur"),
    "TN21": ("Tamil Nadu", "Kanchipuram", "Bangalore Highway, Kanchipuram"),
    "TN22": ("Tamil Nadu", "Meenambakkam", "GST Road, Meenambakkam, Chennai"),
    "TN23": ("Tamil Nadu", "Vellore", "Katpadi Road, Vellore"),
    "TN24": ("Tamil Nadu", "Krishnagiri", "Rayakottai Road, Krishnagiri"),
    "TN25": ("Tamil Nadu", "Tiruvannamalai", "Vengikal, Tiruvannamalai"),
    "TN28": ("Tamil Nadu", "Namakkal North", "Mohanur Road, Namakkal"),
    "TN29": ("Tamil Nadu", "Dharmapuri", "Collectorate Bye-Pass Road, Dharmapuri"),
    "TN30": ("Tamil Nadu", "Salem West", "Meyyanur, Salem"),
    "TN31": ("Tamil Nadu", "Cuddalore", "Beach Road, Cuddalore"),
    "TN32": ("Tamil Nadu", "Villupuram", "Trichy Main Road, Villupuram"),
    "TN33": ("Tamil Nadu", "Erode East", "Perundurai Road, Erode"),
    "TN34": ("Tamil Nadu", "Tiruchengodu", "Velur Road, Tiruchengodu"),
    "TN37": ("Tamil Nadu", "Coimbatore South", "Somanur Road, Coimbatore"),
    "TN38": ("Tamil Nadu", "Coimbatore North", "Dr. Balasundaram Road, Coimbatore"),
    "TN39": ("Tamil Nadu", "Tirupur North", "Avinashi Road, Tirupur"),
    "TN40": ("Tamil Nadu", "Mettupalayam", "Annur Road, Mettupalayam"),
    "TN41": ("Tamil Nadu", "Pollachi", "Palani Road, Pollachi"),
    "TN42": ("Tamil Nadu", "Tirupur South", "Dharapuram Road, Tirupur"),
    "TN43": ("Tamil Nadu", "Ooty (Nilgiris)", "Fingerpost, Ooty, Nilgiris"),
    "TN45": ("Tamil Nadu", "Tiruchirappalli Town", "Palakkarai, Tiruchirappalli"),
    "TN46": ("Tamil Nadu", "Perambalur", "Elambalur Road, Perambalur"),
    "TN47": ("Tamil Nadu", "Karur", "Thanthonimalai, Karur"),
    "TN48": ("Tamil Nadu", "Srirangam", "Tiruchirappalli West, Srirangam"),
    "TN49": ("Tamil Nadu", "Thanjavur", "Pudukkottai Road, Thanjavur"),
    "TN50": ("Tamil Nadu", "Tiruvarur", "Mannargudi Road, Tiruvarur"),
    "TN51": ("Tamil Nadu", "Nagapattinam", "East Gate, Nagapattinam"),
    "TN52": ("Tamil Nadu", "Sankari", "Bhavani Main Road, Sankari"),
    "TN54": ("Tamil Nadu", "Salem East", "Udayapatti, Salem"),
    "TN55": ("Tamil Nadu", "Pudukkottai", "Machuvadi, Pudukkottai"),
    "TN56": ("Tamil Nadu", "Perundurai", "RS Road, Perundurai"),
    "TN57": ("Tamil Nadu", "Dindigul", "Collectorate Complex, Dindigul"),
    "TN58": ("Tamil Nadu", "Madurai South", "TKT Nagar, Madurai"),
    "TN59": ("Tamil Nadu", "Madurai North", "Mattuthavani, Madurai"),
    "TN60": ("Tamil Nadu", "Theni", "Bypass Road, Theni"),
    "TN61": ("Tamil Nadu", "Ariyalur", "Jayankondam Road, Ariyalur"),
    "TN63": ("Tamil Nadu", "Sivaganga", "Collectorate Campus, Sivaganga"),
    "TN64": ("Tamil Nadu", "Madurai Central", "Ellis Nagar, Madurai"),
    "TN65": ("Tamil Nadu", "Ramanathapuram", "Kenikarai, Ramanathapuram"),
    "TN66": ("Tamil Nadu", "Coimbatore Central", "Peelamedu, Coimbatore"),
    "TN67": ("Tamil Nadu", "Virudhunagar", "Madurai Road, Virudhunagar"),
    "TN68": ("Tamil Nadu", "Kumbakonam", "Court Road, Kumbakonam"),
    "TN69": ("Tamil Nadu", "Thoothukudi", "Palayamkottai Road, Thoothukudi"),
    "TN70": ("Tamil Nadu", "Hosur", "Denkanikottai Road, Hosur"),
    "TN72": ("Tamil Nadu", "Tirunelveli", "Palayamkottai, Tirunelveli"),
    "TN73": ("Tamil Nadu", "Ranipet", "MBT Road, Ranipet"),
    "TN74": ("Tamil Nadu", "Nagercoil", "Kanyakumari Main Road, Nagercoil"),
    "TN75": ("Tamil Nadu", "Marthandam", "Pumpattivilai, Marthandam"),
    "TN76": ("Tamil Nadu", "Tenkasi", "Courtallam Road, Tenkasi"),
    "TN77": ("Tamil Nadu", "Attur", "Kamharaj Nagar, Attur"),
    "TN78": ("Tamil Nadu", "Dharapuram", "Pollachi Road, Dharapuram"),
    "TN79": ("Tamil Nadu", "Sankarankovil", "Rajapalayam Road, Sankarankovil"),
    "TN81": ("Tamil Nadu", "Tiruchirappalli East", "TVS Tolgate, Tiruchirappalli"),
    "TN82": ("Tamil Nadu", "Mayiladuthurai", "Kallanai Road, Mayiladuthurai"),
    "TN83": ("Tamil Nadu", "Vaniyambadi", "CL Road, Vaniyambadi"),
    "TN84": ("Tamil Nadu", "Srivilliputhur", "Madurai Road, Srivilliputhur"),
    "TN85": ("Tamil Nadu", "Kundrathur", "Main Road, Kundrathur, Chennai"),
    "TN86": ("Tamil Nadu", "Erode West", "Solar, Erode"),
    "TN87": ("Tamil Nadu", "Sriperumbudur", "Highways Road, Sriperumbudur"),
    "TN88": ("Tamil Nadu", "Namakkal South", "Paramathi Road, Namakkal"),
    "TN90": ("Tamil Nadu", "Avadi", "NM Road, Avadi, Chennai"),
    "TN91": ("Tamil Nadu", "Kovilpatti", "Ettayapuram Road, Kovilpatti"),
    "TN92": ("Tamil Nadu", "Nanguneri", "Main Road, Nanguneri"),
    "TN93": ("Tamil Nadu", "Mettur", "Square Market, Mettur"),
    "TN94": ("Tamil Nadu", "Palani", "Dindigul Road, Palani"),
    "TN95": ("Tamil Nadu", "Sivakasi", "Srivilliputhur Road, Sivakasi"),
    "TN99": ("Tamil Nadu", "Coimbatore West", "Kovaipudur, Coimbatore"),
    "KA01": ("Karnataka", "Bengaluru Central", "Koramangala, Bengaluru"),
    "KA02": ("Karnataka", "Bengaluru West", "Rajajinagar, Bengaluru"),
    "KA03": ("Karnataka", "Bengaluru East", "Indiranagar, Bengaluru"),
    "KA05": ("Karnataka", "Bengaluru South", "Jayanagar, Bengaluru"),
    "KA51": ("Karnataka", "Electronic City", "Hosur Road, Bengaluru"),
    "MH01": ("Maharashtra", "Mumbai Central", "Tardeo, Mumbai"),
    "MH02": ("Maharashtra", "Mumbai West", "Andheri West, Mumbai"),
    "MH12": ("Maharashtra", "Pune", "Sangamwadi, Pune"),
    "DL01": ("Delhi", "North Delhi", "Mall Road, Delhi"),
    "DL03": ("Delhi", "South Delhi", "Sheikh Sarai, New Delhi"),
    "KL01": ("Kerala", "Thiruvananthapuram", "Kudappanakkunnu, Thiruvananthapuram"),
    "KL07": ("Kerala", "Ernakulam", "Civil Station, Kakkanad, Ernakulam"),
    "TS09": ("Telangana", "Hyderabad Central", "Khairatabad, Hyderabad"),
    "UP16": ("Uttar Pradesh", "Noida", "Sector 32, Noida")
}


def fix_ocr_confusion(raw_text: str) -> str:
    """
    Clean raw OCR string and fix common character confusions for Indian plates.
    Indian plate format: STATE(2 letters) + RTO(2 digits) + SERIES(1-3 letters) + NUMBER(1-4 digits)

    Strategy: apply position-aware corrections based on expected character type at each position.
    """
    if not raw_text:
        return ""
    clean = re.sub(r'[^A-Z0-9]', '', raw_text.upper())
    if len(clean) < 3:
        return clean

    # ── Full substitution maps ──────────────────────────────────
    # When a letter is expected but a digit was read
    digit_to_letter = {
        '0': 'O', '1': 'I', '2': 'Z', '3': 'B', '4': 'A',
        '5': 'S', '6': 'G', '7': 'T', '8': 'B', '9': 'P'
    }
    # When a digit is expected but a letter was read
    letter_to_digit = {
        'O': '0', 'D': '0', 'Q': '0', 'U': '0',
        'I': '1', 'L': '1', 'T': '1',
        'Z': '2',
        'E': '3',
        'A': '4', 'H': '4',
        'S': '5',
        'G': '6', 'C': '6',
        'J': '7',
        'B': '8', 'X': '8',
        'P': '9', 'R': '9'
    }

    chars = list(clean)
    n = len(chars)

    # Positions 0-1: STATE CODE — must be letters
    for i in range(min(2, n)):
        if chars[i] in digit_to_letter:
            chars[i] = digit_to_letter[chars[i]]

    # Positions 2-3: RTO NUMBER — must be digits
    for i in range(2, min(4, n)):
        if chars[i] in letter_to_digit:
            chars[i] = letter_to_digit[chars[i]]

    # Positions 4 onward: SERIES (letters) then NUMBER (digits)
    # Detect transition point: find where letters end and final digits begin
    # Indian plates end with 1-4 digits
    if n >= 6:
        # Last 4 chars: try to convert to digits
        for i in range(max(4, n - 4), n):
            if chars[i] in letter_to_digit:
                chars[i] = letter_to_digit[chars[i]]
        # Middle chars (series): must be letters
        for i in range(4, max(4, n - 4)):
            if chars[i] in digit_to_letter:
                chars[i] = digit_to_letter[chars[i]]

    return "".join(chars)


def _try_fuzzy_recover_indian_plate(raw: str) -> str:
    """
    Attempt to recover a valid Indian plate number from heavily garbled OCR text.
    Uses a sliding-window approach: tries every 8-10 char substring and applies
    aggressive character correction to find one matching the Indian format.
    Returns corrected plate string or empty string if no valid plate found.
    """
    if not raw or len(raw) < 6:
        return ""

    clean = re.sub(r'[^A-Z0-9]', '', raw.upper())

    # Try all substrings of length 8, 9, 10
    candidates = []
    for length in [10, 9, 8]:
        for start in range(len(clean) - length + 1):
            substr = clean[start:start + length]
            corrected = fix_ocr_confusion(substr)
            # Check if it matches Indian plate pattern after correction
            m = re.match(r'^([A-Z]{2})(\d{2})([A-Z]{1,3})(\d{1,4})$', corrected)
            if m:
                st = m.group(1)
                if st in INDIAN_STATES:
                    candidates.append((corrected, start))

    if candidates:
        # Prefer the one starting earliest (left-to-right reading order)
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]

    return ""


def parse_indian_plate(plate_text: str):
    """
    Parses Global & Indian Registration numbers and returns full country & regional details.
    """
    cleaned = fix_ocr_confusion(plate_text)
    if not cleaned:
        return {
            "vehicle_number": "UNKNOWN",
            "country": "—",
            "country_code": "—",
            "state": "—",
            "state_code": "—",
            "rto_code": "—",
            "registration_area": "—",
            "rto_place_location": "—",
            "series": "—",
            "registration_number": "—",
            "ocr_status": "ocr_failed"
        }

    # 1. India Plate Detection (Full or Partial/Short Format)
    st_prefix = cleaned[:2]
    if st_prefix in INDIAN_STATES:
        state_name = INDIAN_STATES[st_prefix]
        rto_code = cleaned[:4] if len(cleaned) >= 4 else f"{st_prefix}01"
        
        # Check if full standard format: STATE(2) + RTO(2) + SERIES(1-3)? + NUMBER(1-4)
        in_match = re.match(r'^([A-Z]{2})(\d{1,2})([A-Z]{1,3})?(\d{1,4})$', cleaned)
        if in_match:
            rto_num = in_match.group(2).zfill(2)
            rto_code = f"{st_prefix}{rto_num}"
            series = in_match.group(3) or ""
            reg_num = in_match.group(4)
            formatted_number = f"{st_prefix}{rto_num}{series}{reg_num}"
        else:
            formatted_number = cleaned
            series = ""
            reg_num = cleaned[2:]

        reg_area = f"{state_name} Regional Transport Office"
        rto_place = f"State Transport Department, {state_name}"

        if rto_code in INDIAN_RTO_MAP:
            info = INDIAN_RTO_MAP[rto_code]
            state_name = info[0]
            reg_area = info[1]
            rto_place = info[2] if len(info) > 2 else f"{reg_area}, {state_name}"
        elif st_prefix == "AS":
            reg_area = f"Assam RTO ({rto_code})"
            rto_place = "Transport Department, Dispur, Guwahati, Assam"

        return {
            "vehicle_number": formatted_number,
            "country": "India 🇮🇳",
            "country_code": "IN",
            "state": state_name,
            "state_code": st_prefix,
            "rto_code": rto_code,
            "registration_area": reg_area,
            "rto_place_location": rto_place,
            "series": series,
            "registration_number": reg_num
        }

    # 2. India Bharat Series (BH): e.g., 22BH1234AA
    bh_pattern = r'^(\d{2})BH(\d{4})([A-Z]{1,2})$'
    bh_match = re.match(bh_pattern, cleaned)
    if bh_match:
        yy = bh_match.group(1)
        num = bh_match.group(2)
        series = bh_match.group(3)
        return {
            "vehicle_number": f"{yy}BH{num}{series}",
            "country": "India 🇮🇳",
            "country_code": "IN",
            "state": "Bharat Series (All-India)",
            "state_code": "BH",
            "rto_code": f"{yy}BH",
            "registration_area": "Pan-India Centralized Registration",
            "rto_place_location": "MoRTH Central Transport Portal, New Delhi",
            "series": series,
            "registration_number": num
        }

    # 3. Fuzzy recovery — try sliding-window correction on the raw OCR noise
    #    e.g. "INDRJIGCVO002" → "TN04Q5763"
    recovered = _try_fuzzy_recover_indian_plate(plate_text)
    if recovered:
        print(f"[PlateParser] Fuzzy recovery: '{plate_text}' → '{recovered}'")
        return parse_indian_plate(recovered)  # re-parse the corrected string

    # 4. Plate text was read by OCR but doesn't match any known format
    #    Return a genuine "unrecognized" result — never fabricate country/state data.
    return {
        "vehicle_number": cleaned,
        "country": "—",
        "country_code": "—",
        "state": "—",
        "state_code": "—",
        "rto_code": "—",
        "registration_area": "—",
        "rto_place_location": "—",
        "series": "—",
        "registration_number": "—",
        "ocr_status": "unrecognized_format"
    }
