import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, cohen_kappa_score

import controller
import functii
from grafice import plot_instante, distributie
from gui import *


class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.model_creat = False
        self.model_creat_ = False
        self.director = "."
        self.buton_citire1.clicked.connect(self.citire1)
        self.buton_selectie.clicked.connect(lambda x: controller.selectie_generala(self.list_variabile))
        self.buton_citire2.clicked.connect(self.citire2)
        self.buton_acuratete.clicked.connect(self.afisare_acuratete)
        self.buton_clasificare1.clicked.connect(self.clasificare1)
        self.buton_acuratete_.clicked.connect(self.afisare_acuratete_)
        self.buton_clasificare1_.clicked.connect(self.clasificare1_)
        self.buton_clasificare2.clicked.connect(self.clasificare2)
        self.buton_clasificare2_.clicked.connect(self.clasificare2_)
        self.buton_plot.clicked.connect(self.plot_instante)
        self.buton_plot_distrib.clicked.connect(self.plot_distributie)
        self.buton_predictori.clicked.connect(self.putere_predictori)
        self.buton_distrib_predictori.clicked.connect(self.plot_distributie_predictori)
        self.pushButton.clicked.connect(self.putere_discriminatori)

    def plot_distributie_predictori(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        x = self.t[self.variabile_predictor].values
        m = x.shape[1]
        for i in range(m):
            distributie(x, i, self.y, self.clase, self.variabile_predictor[i])

    def putere_predictori(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        putere_discriminare_x = pd.DataFrame(
            data={
                'Putere Discriminare': self.l_x, 'p_values': np.around(self.p_values, 2)
            }, index=self.variabile_predictor
        )
        putere_discriminare_x.to_csv("Putere_disc_predictori.csv")
        dialog = controller.DialogNonModal(self, putere_discriminare_x, titlu="Putere discriminare predictori")
        dialog.show()

    def putere_discriminatori(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        q = len(self.clase)
        n = len(self.y)
        putere_discriminare = pd.DataFrame(
            data={
                'Putere_disc': self.l,
                'Putere_disc(%)': self.l * 100 / sum(self.l),
                'Putere_disc_cumulata(%)': np.cumsum(self.l) * 100 / sum(self.l),
                'alpha': self.alpha,
                'p_value': 1.0 - functii.sts.f.cdf(self.l, q - 1, n - q)
            }, index=self.z_index
        )
        putere_discriminare.to_csv("Putere_disc.csv")
        dialog = controller.DialogNonModal(self, putere_discriminare, titlu="Putere discriminare discriminatori")
        dialog.show()

    def plot_distributie(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        for i in range(self.nr_axe):
            distributie(self.z, i, self.y, self.clase)

    def plot_instante(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        if self.nr_axe > 1:
            for i in range(1, self.nr_axe):
                plot_instante(self.z, 0, i, self.zg, self.y, self.clase)
        else:
            self.text_out.append("Numar insuficient de axe (" + str(self.nr_axe) + ")")

    def clasificare2_(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        t_clasif = pd.DataFrame(
            data={
                "Predictie LDA": self.y_predict_test_
            }, index=self.t_.index
        )
        t_clasif.to_csv("Predict_LDA.csv")
        dialog = controller.DialogNonModal(self, t_clasif, titlu="Clsificare in setul de aplicare (LDA)")
        dialog.show()

    def clasificare2(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        t_clasif = pd.DataFrame(
            data={
                "Predictie Bayes": self.y_predict_test
            }, index=self.t_.index
        )
        t_clasif.to_csv("Predict_Bayes.csv")
        dialog = controller.DialogNonModal(self, t_clasif, titlu="Clsificare in setul de aplicare (Bayes)")
        dialog.show()

    def clasificare1(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        t_clasif = pd.DataFrame(
            data={
                self.variabila_tinta: self.y,
                "Predictie Bayes": self.y_predict
            }, index=self.instante
        )
        t_clasif.to_csv("Predict_set_antrenare_Bayes.csv")
        dialog = controller.DialogNonModal(self, t_clasif, titlu="Clsificare in setul de antrenare")
        dialog.show()

    def clasificare1_(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        t_clasif = pd.DataFrame(
            data={
                self.variabila_tinta: self.y,
                "Predictie LDA": self.y_predict_
            }, index=self.instante
        )
        t_clasif.to_csv("Predict_set_antrenare_LDA.csv")
        dialog = controller.DialogNonModal(self, t_clasif, titlu="Clsificare in setul de antrenare (LDA)")
        dialog.show()

    def afisare_acuratete_(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        n = len(self.t)
        acuratete_globala = np.round(sum(np.diagonal(self.mat_conf_)) * 100 / n, 3)
        acuratete_grupe = np.round(np.diagonal(self.mat_conf_) * 100 / np.sum(self.mat_conf_, axis=1))
        acuratete_medie = np.mean(acuratete_grupe)
        t_matconf = pd.DataFrame(self.mat_conf_, self.clase, self.clase)
        t_matconf["Acuratete"] = acuratete_grupe
        self.text_out.append("Acuratete globala (LDA):" + str(acuratete_globala))
        self.text_out.append("Acuretete medie (LDA):" + str(acuratete_medie))
        self.text_out.append("Inxex Kappa-Kohen (LDA):" + str(self.index_cohen_kappa_))
        t_matconf.to_csv("mat_conf_LDA.csv")

        dialog = controller.DialogNonModal(self, t_matconf, titlu="Matrice confuzie (LDA)")
        dialog.show()

    def afisare_acuratete(self):
        if not self.model_creat_:
            if not self.creare_model_():
                return
        n = len(self.t)
        acuratete_globala = np.round(sum(np.diagonal(self.mat_conf)) * 100 / n, 3)
        acuratete_grupe = np.round(np.diagonal(self.mat_conf) * 100 / np.sum(self.mat_conf, axis=1))
        acuratete_medie = np.mean(acuratete_grupe)
        t_matconf = pd.DataFrame(self.mat_conf, self.clase, self.clase)
        t_matconf["Acuratete"] = acuratete_grupe
        self.text_out.append("Acuratete globala (Bayes):" + str(acuratete_globala))
        self.text_out.append("Acuretete medie (Bayes):" + str(acuratete_medie))
        self.text_out.append("Inxex Kappa-Kohen (Bayes):" + str(self.index_cohen_kappa))
        t_matconf.to_csv("mat_conf_Bayes.csv")

        dialog = controller.DialogNonModal(self, t_matconf, titlu="Matrice confuzie (Bayes)")
        dialog.show()

    def date_citite(self):
        if not self.text_fisier1.text() or not self.text_fisier2.text():
            return False
        return True

    def creare_model_(self):
        if not self.date_citite():
            msgBox = QMessageBox()
            msgBox.setText("Nu au fost citite seturile de date!")
            msgBox.exec()
            return False
        variabila_index = self.combo_index.currentText()
        self.t.index = self.t[variabila_index]
        self.variabile_predictor = controller.selectii_lista(self.list_variabile)
        self.variabila_tinta = self.combo_tinta.currentText()
        self.instante = list(self.t.index)

        x = self.t[self.variabile_predictor].values
        self.y = self.t[self.variabila_tinta].values
        n = x.shape[0]
        self.clase, self.p, g, sst, ssb, ssw = functii.imprastiere(x, self.y)
        q = len(self.clase)
        # Calcul putere de discriminare variabile predictor
        self.l_x, self.p_values = functii.putere_discriminare(ssb, ssw, n, q)
        self.alpha, self.l, u = functii.lda(sst, ssb, n, q)
        self.nr_axe = np.shape(u)[1]
        self.z = x @ u
        self.zg = g @ u
        # Functii clasif
        f, f0, f0_b = functii.functii_clasificare_z(self.z, self.zg, self.p)
        self.z_index = ['z' + str(i) for i in range(1, self.nr_axe + 1)]

        t_functii = functii.tabelare_matrice(f,self.clase,self.z_index)
        t_functii["Intercept LDA"] = f0
        t_functii["Intercept Bayes"] = f0_b
        t_functii.to_csv("Functii_clasif.csv")
        # predictie pe baza functiilor de clasificare lda
        self.y_predict_ = functii.predict(self.z, f, f0, self.clase)
        # predictie pe baza functiilor de clasificare bayes
        self.y_predict = functii.predict(self.z, f, f0_b, self.clase)

        self.mat_conf_ = confusion_matrix(self.y, self.y_predict_)
        self.index_cohen_kappa_ = cohen_kappa_score(self.y, self.y_predict_)
        self.mat_conf = confusion_matrix(self.y, self.y_predict)
        self.index_cohen_kappa = cohen_kappa_score(self.y, self.y_predict)

        x_ = self.t_[self.variabile_predictor].values
        z = x_ @ u
        self.y_predict_test_ = functii.predict(z, f, f0, self.clase)
        self.y_predict_test = functii.predict(z, f, f0_b, self.clase)

        self.model_creat_ = True
        return True

    def citire1(self):
        rez = controller.citire_fisier_variabile(self.director, self.combo_index, self.list_variabile)
        if rez is not None:
            self.t = rez[0]
            self.text_fisier1.setText(rez[1])
            controller.init_combo(self.combo_tinta, list(self.t))
            self.director = rez[1][:rez[1].rfind("/")]
        self.invalidare_modele()
        self.schimbare_parametri()

    def citire2(self):
        rez = controller.citire_fisier(self.director)
        if rez is not None:
            self.t_ = rez[0]
            self.text_fisier2.setText(rez[1])
        self.invalidare_modele()

    def schimbare_parametri(self):
        self.combo_tinta.currentTextChanged.connect(self.invalidare_modele)
        for i in range(self.list_variabile.count()):
            item = self.list_variabile.item(i)
            check = self.list_variabile.itemWidget(item)
            check.stateChanged.connect(self.invalidare_modele)

    def invalidare_modele(self):
        self.model_creat_ = False
