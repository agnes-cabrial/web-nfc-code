import nfc
import ndef

def write_nfc_tag(url):
    clf = nfc.ContactlessFrontend()

    if not clf.open("usb"):
        print("NFC Reader Not Found")
        return

    print("Waiting for NFC Tag... new file")

    tag = clf.connect(rdwr={'on-connect': lambda tag: False})

    if tag.ndef:
        record = ndef.UriRecord(url)
        tag.ndef.records = [record]
        print(f"URL Written to NFC: {url}")
    else:
        print("NFC Tag not supported")

    clf.close()
