from io import BytesIO

import qrcode
import qrcode.image.svg


def crc16_ccitt(data: str) -> str:
    crc = 0xFFFF
    for char in data.encode("utf-8"):
        crc ^= char << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def format_tlv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def generate_pix_payload(
    pix_key: str, merchant_name: str, merchant_city: str, amount: float
) -> str:
    # Sanitize strings to meet Banco Central limits
    name = merchant_name.strip().upper()[:25]
    city = merchant_city.strip().upper()[:15]
    amount_str = f"{amount:.2f}"

    # Build Merchant Account Information (Tag 26)
    gui = format_tlv("00", "br.gov.bcb.pix")
    key = format_tlv("01", pix_key.strip())
    merchant_info = format_tlv("26", gui + key)

    # Assemble core EMV fields
    payload = (
        format_tlv("00", "01")  # Payload Format Indicator
        + merchant_info  # Pix Key Info
        + format_tlv("52", "0000")  # Merchant Category Code
        + format_tlv("53", "986")  # Currency (986 = BRL)
        + format_tlv("54", amount_str)  # Transaction Amount
        + format_tlv("58", "BR")  # Country Code
        + format_tlv("59", name)  # Merchant Name
        + format_tlv("60", city)  # Merchant City
        + format_tlv("62", format_tlv("05", "***"))  # Additional Data (TxID)
        + "6304"  # CRC16 Tag & Length
    )

    return payload + crc16_ccitt(payload)


def generate_pix_svg(payload: str) -> str:
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(payload, image_factory=factory, box_size=8)
    stream = BytesIO()
    img.save(stream)
    return stream.getvalue().decode("utf-8")
