# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 12:26:01 2023

@author: Franz Ostler
"""

import numpy as np
import cv2
import glob

feldanzahl_schachbrett = 0

def kalibriere_kamera():
    schachbrett_größe = (feldanzahl_schachbrett-1, feldanzahl_schachbrett-1)  # Größe des Schachbrettmusters
    schachbrettmuster_punkte = []  # 3D-Koordinaten des Schachbrettmusters
    bilder_punkte = []  # 2D-Koordinaten des Schachbrettmusters in den Bildern

    # Erzeugen der 3D-Koordinaten des Schachbrettmusters
    for i in range(schachbrett_größe[1]):
        for j in range(schachbrett_größe[0]):
            schachbrettmuster_punkte.append((j, i, 0))

    bilder = glob.glob('path/*.jpg')  # Liste der Bildpfade

    for bild_pfad in bilder:
        bild = cv2.imread(bild_pfad)
        grau = cv2.cvtColor(bild, cv2.COLOR_BGR2GRAY)

        # Suchen der Eckpunkte des Schachbrettmusters im Bild
        ret, ecken = cv2.findChessboardCorners(grau, schachbrett_größe, None)

        if ret:
            schachbrettmuster_punkte.append(schachbrettmuster_punkte)
            bilder_punkte.append(ecken)

    ret, matrix, dist_koeff, rvecs, tvecs = cv2.calibrateCamera(
        schachbrettmuster_punkte, bilder_punkte, grau.shape[::-1], None, None
    )

    return matrix, dist_koeff, bilder_punkte

def kalibriere_beide_Kameras(objectPoints, cameraMatrix1, distCoeffs1, imageSize, imagePoints1):
    
    # Abstand zwischen den Kameras
    baseline = 50.0  # 50 cm
    
    # Setzen des Translationsvektors für die zweite Kamera
    translationVector2 = np.array([[baseline, 0, 0]], dtype=np.float64)
    
    # Kalibrierung der zweiten Kamera
    (_, _, _, _, _, rotationMatrix2, _, _, _) = cv2.calibrateCamera(
        objectPoints, imagePoints1, imageSize,
        cameraMatrix1, distCoeffs1,
        rvecs=None, tvecs=None,
        flags=cv2.CALIB_FIX_INTRINSIC
    )
    
    # Extrinsische Parameter für die zweite Kamera
    rotationMatrix2 = rotationMatrix2[0]  # Extrahieren der RotationsmatrixranslationVector * versatz
    
    return translationVector2, rotationMatrix2