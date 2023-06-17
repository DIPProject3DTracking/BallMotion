# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 14:45:13 2023

@author: Franz Ostler
"""
import numpy as np

from calibrate import kalibriere_kamera, kalibriere_beide_Kameras

matrix1, distkoeff1, bildpt1 = kalibriere_kamera()
transl2, rot2 = kalibriere_beide_Kameras(matrix1, distkoeff1, bildpt1)

np.savetxt("intrinsische_matrix_left_camera.txt", matrix1)
np.savetxt("translationsvektor_right_camera.txt", transl2)
np.savetxt("rotationsvektor_right_camera.txt", rot2)