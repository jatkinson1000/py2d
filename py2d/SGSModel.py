import jax.numpy as np
import numpy as nnp

from py2d.eddy_viscosity_models import eddy_viscosity_smag, characteristic_strain_rate_smag, coefficient_dsmag_PsiOmega
from py2d.eddy_viscosity_models import eddy_viscosity_leith, characteristic_omega_leith, coefficient_dleith_PsiOmega
from py2d.gradient_model import GM2, GM4, GM6
# from py2d.uv2tau_CNN import evaluate_model, init_model
from py2d.convert import *

class SGSModel:
    
    def __init__(self, method = 'NoSGS'):
        self.set_method(method)

    def set_method(self, method):
        if method == 'NoSGS':
            self.calculate = self.no_sgs_method
        elif method == 'SMAG':
            self.calculate = self.smag_method
        elif method == 'DSMAG':
            self.calculate = self.dsmag_method
        elif method == 'LEITH':
            self.calculate = self.leith_method
        elif method == 'DLEITH':
            self.calculate = self.dleith_method
        elif method == 'PiOmegaGM2':
            self.calculate = self.PiOmegaGM2_method
        elif method == 'PiOmegaGM4':
            self.calculate = self.PiOmegaGM4_method
        elif method == 'PiOmegaGM6':
            self.calculate = self.PiOmegaGM6_method
        elif method == 'CNN':
            self.calculate = self.cnn_method
        elif method == 'GAN':
            self.calculate = self.gan_method
        else:
            raise ValueError(f"Invalid method: {method}")


    def no_sgs_method(self):
        PiOmega_hat = 0.0
        eddy_viscosity = 0.0
        return PiOmega_hat, eddy_viscosity

    
    def smag_method(self, Psi_hat, Kx, Ky, Ksq, Cs, Delta):
        PiOmega_hat = 0.0
        characteristic_S = characteristic_strain_rate_smag(Psi_hat, Kx, Ky, Ksq)
        eddy_viscosity = eddy_viscosity_smag(Cs, Delta, characteristic_S)
        return PiOmega_hat, eddy_viscosity, Cs

    
    def leith_method(self, Omega_hat, Kx, Ky, Cl, Delta):
        PiOmega_hat = 0.0
        characteristic_Omega = characteristic_omega_leith(Omega_hat, Kx, Ky)
        eddy_viscosity = eddy_viscosity_leith(Cl, Delta, characteristic_Omega)
        return PiOmega_hat, eddy_viscosity, Cl

    
    def dsmag_method(self, Psi_hat, Omega_hat, Kx, Ky, Ksq, Delta):
        PiOmega_hat = 0.0
        characteristic_S = characteristic_strain_rate_smag(Psi_hat, Kx, Ky, Ksq)
        c_dynamic = coefficient_dsmag_PsiOmega(Psi_hat, Omega_hat, characteristic_S, Kx, Ky, Ksq, Delta)
        Cs = np.sqrt(c_dynamic)
        eddy_viscosity = eddy_viscosity_smag(Cs, Delta, characteristic_S)
        return PiOmega_hat, eddy_viscosity, Cs

    def dleith_method(self, Psi_hat, Omega_hat, Kx, Ky, Ksq, Delta):
        PiOmega_hat = 0.0
        characteristic_Omega = characteristic_omega_leith(Omega_hat, Kx, Ky)
        c_dynamic = coefficient_dleith_PsiOmega(Psi_hat, Omega_hat, characteristic_Omega, Kx, Ky, Ksq, Delta)
        Cl = c_dynamic ** (1/3)
        eddy_viscosity = eddy_viscosity_leith(Cl, Delta, characteristic_Omega)
        return PiOmega_hat, eddy_viscosity, Cl

    def PiOmegaGM2_method(self, Omega_hat, U_hat, V_hat, Kx, Ky, Delta):
        eddy_viscosity = 0
        PiOmega = GM2(Omega_hat=Omega_hat, U_hat=U_hat, V_hat=V_hat, Kx=Kx, Ky=Ky, Delta=Delta)
        PiOmega_hat = np.fft.fft2(PiOmega)
        return PiOmega_hat, eddy_viscosity

    def PiOmegaGM4_method(self, Omega_hat, U_hat, V_hat, Kx, Ky, Delta):
        eddy_viscosity = 0
        PiOmega = GM4(Omega_hat=Omega_hat, U_hat=U_hat, V_hat=V_hat, Kx=Kx, Ky=Ky, Delta=Delta)
        PiOmega_hat = np.fft.fft2(PiOmega)
        return PiOmega_hat, eddy_viscosity
    
    def PiOmegaGM6_method(self, Omega_hat, U_hat, V_hat, Kx, Ky, Delta):
        eddy_viscosity = 0
        PiOmega = GM6(Omega_hat=Omega_hat, U_hat=U_hat, V_hat=V_hat, Kx=Kx, Ky=Ky, Delta=Delta)
        PiOmega_hat = np.fft.fft2(PiOmega)
        return PiOmega_hat, eddy_viscosity
    
    def cnn_method(self, model, input_data, Kx, Ky, Ksq):
        """Perform the CNN calculation."""
        
        # U_hat, V_hat = Psi2UV_2DFHIT(Psi1_hat, Kx, Ky, Ksq)
        # U = np.real(np.fft.ifft2(U_hat))
        # V = np.real(np.fft.ifft2(V_hat))
        # input_data = np.stack((U, V), axis=0)
        output = evaluate_model(model, input_data)

        # Tau11CNN_hat = np.fft.fft2(output[0])
        # Tau12CNN_hat = np.fft.fft2(output[1])
        # Tau22CNN_hat = np.fft.fft2(output[2])
        
        # PiOmega_hat = Tau2PiOmega_2DFHIT(Tau11CNN_hat, Tau12CNN_hat, Tau22CNN_hat, Kx, Ky, Ksq)
        
        return output

    
    def gan_method(self, data):
        # Implement GAN method
        return "Calculated with GAN method"
    
# Usage example:

# model = PiOmegaModel()  # Default method is NO-SGS
# model.set_method('CNN')
# result = model.calculate("Sample Data")
# print(result)  # Output: Calculated with NO-SGS method
