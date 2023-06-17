"""
Created on Sat Jun 17 12:26:01 2023

@author: Franz Ostler
"""
import numpy as np
import cv2
import glob

def kalibriere_kamera(feldanzahl_schachbrett = 8):
    schachbrett_größe = (feldanzahl_schachbrett-1, feldanzahl_schachbrett-1)  # Größe des Schachbrettmusters
    schachbrettmuster_punkte = []  # 3D-Koordinaten des Schachbrettmusters
    bilder_punkte = []  # 2D-Koordinaten des Schachbrettmusters in den Bildern

    # Erzeugen der 3D-Koordinaten des Schachbrettmusters
    for i in range(schachbrett_größe[1]):
        for j in range(schachbrett_größe[0]):
            schachbrettmuster_punkte.append((j, i, 0))

    bilder = glob.glob('calibration_pictures/*.jpg')  # Liste der Bildpfade

    for bild_pfad in bilder:
        bild = cv2.imread(bild_pfad)
        grau = cv2.cvtColor(bild, cv2.COLOR_BGR2GRAY)

        # Suchen der Eckpunkte des Schachbrettmusters im Bild
        ret, ecken = cv2.findChessboardCorners(grau, schachbrett_größe, None)

        if ret:
            schachbrettmuster_punkte.append(np.float32(schachbrettmuster_punkte))
            bilder_punkte.append(ecken)

    ret, matrix, dist_koeff, rvecs, tvecs = cv2.calibrateCamera(
        schachbrettmuster_punkte, bilder_punkte, grau.shape[::-1], None, None
    )
    np.savetxt("object_points.txt", np.float32(schachbrettmuster_punkte))
    return matrix, dist_koeff, bilder_punkte

def kalibriere_beide_Kameras(cameraMatrix1, distCoeffs1, imagePoints1, imageSize=(640, 480), objectPoints=np.loadtxt("object_points.txt")):
    # Abstand zwischen den Kameras
    baseline = 50.0  # 50 cm
    
    # Setzen des Translationsvektors für die zweite Kamera
    translationVector2 = np.array([[baseline, 0, 0]], dtype=np.float64)
    
    # Kalibrierung der zweiten Kamera
    (_, _, _, rotationMatrix2, _, _) = cv2.calibrateCamera(
        objectPoints, imagePoints1, imageSize,
        cameraMatrix1, distCoeffs1,
        flags=cv2.CALIB_FIX_INTRINSIC
    )
    
    # Extrinsische Parameter für die zweite Kamera
    rotationMatrix2 = rotationMatrix2[0]  # Extrahieren der Rotationsmatrix
    
    return translationVector2, rotationMatrix2