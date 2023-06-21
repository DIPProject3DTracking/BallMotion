import cv2
import os
from datetime import datetime

# Ordner zum Speichern der Bilder
output_folder = "calibration_pictures"

# Erstellen Sie den Ordner, wenn er nicht vorhanden ist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Öffnen Sie die Webcam
cap = cv2.VideoCapture(1)  # 0 steht für die erste angeschlossene Kamera, können Sie anpassen, wenn mehrere Kameras angeschlossen sind

# Überprüfen Sie, ob die Webcam erfolgreich geöffnet wurde
if not cap.isOpened():
    print("Fehler beim Öffnen der Webcam")
    exit()

# Schleife zum Aufnehmen von Bildern
while True:
    # Lesen Sie das aktuelle Bild von der Webcam
    ret, frame = cap.read()

    # Überprüfen Sie, ob das Bild erfolgreich erfasst wurde
    if not ret:
        print("Fehler beim Erfassen des Bildes von der Webcam")
        break

    # Zeigen Sie das Bild an
    cv2.imshow("Webcam", frame)

    # Warten Sie auf die Tasteneingabe "q", um die Schleife zu beenden
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord(" "):
        # Generieren Sie einen eindeutigen Dateinamen basierend auf der aktuellen Zeit
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = os.path.join(output_folder, f"image_{timestamp}.jpg")

        # Speichern Sie das Bild im Ausgabeordner
        cv2.imwrite(image_name, frame)
        print("Bild gespeichert:", image_name)

# Schließen Sie die Webcam und zerstören Sie die Fenster
cap.release()
cv2.destroyAllWindows()