import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.transforms import IdentityTransform  # Um Formeln in Bildet umzuandeln
import numpy as np
import random as rand

from dataclasses import dataclass, field

def create_formula_fig(string):
    # Länge bestimmen
  length = len(string) - string.count("frac")*10
  # Bild erstellen mit variabler Länge
  latex_fig = plt.figure(figsize=(length*0.2, 0.4), dpi=400)
  ax = latex_fig.add_axes([0,0,1,1])
  string = r"$" + string + r"$"
  ax.text(0, 0.5, string, fontsize=14, verticalalignment="center") # transform=IdentityTransform()
  ax.set_axis_off()
  return latex_fig



def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def to_decimal(string):
    """
    Wandelt einen Dezimalstring in:
    [ganze_zahl, nachkommastellen]
    um.

    Beispiel:
    "1.25" -> [125, 2]
    """

    digits = 0

    if "." in string:
        digits = len(string.split(".", 1)[1])

    dec = 0

    for char in string:
        if char.isnumeric():
            dec = dec * 10 + int(char)

    if float(string) < 0:
        dec = -dec

    return [dec, digits]


@dataclass
class QZahl:

    zaehler: int = 1
    nenner: int = 1

    def __post_init__(self):
        self.transform()

    # =========================================================
    # Hilfsmethoden
    # =========================================================

    def copy(self):
        return QZahl(self.zaehler, self.nenner)

    def set(self, zaehler, nenner=1):
        self.zaehler = int(zaehler)
        self.nenner = int(nenner)
        self.transform()

    # =========================================================
    # Parsing
    # =========================================================

    def fromString(self, string):

        string = string.replace(" ", "")
        string = string.replace(",", ".")

        nenner = 1
        digits_n = 0

        # -----------------------------------------------------
        # Bruch erkennen
        # -----------------------------------------------------

        if "frac" in string:

            if r"\.}{\." not in string:
                return string + " ist kein gültiger Bruch"

            string1, string2 = string.split(r"\.}{\.")

            string = string1.replace(r"\frac{\.", "")

            string2, _ = string2.split(r"\.}")

            if not is_float(string2):
                return string2 + " kann nicht in Nenner umgewandelt werden."

            nenner, digits_n = to_decimal(string2)

        elif "/" in string:

            string, string2 = string.split("/", 1)

            if not is_float(string2):
                return string2 + " kann nicht in Nenner umgewandelt werden."

            nenner, digits_n = to_decimal(string2)

        # -----------------------------------------------------
        # Zähler lesen
        # -----------------------------------------------------

        if not is_float(string):
            return string + " kann nicht in Zähler umgewandelt werden."

        zaehler, digits_z = to_decimal(string)

        # -----------------------------------------------------
        # Nachkommastellen beseitigen
        # -----------------------------------------------------

        while digits_n > 0:
            zaehler *= 10
            digits_n -= 1

        while digits_z > 0:
            nenner *= 10
            digits_z -= 1

        self.set(zaehler, nenner)

        return None

    def fromLatexString(self, string):
        return self.fromString(string)

    # =========================================================
    # Eigenschaften
    # =========================================================

    def is_neg(self):
        return self.zaehler < 0

    def is_zero(self):
        return self.zaehler == 0

    def asFloat(self):
        return self.zaehler / self.nenner

    # =========================================================
    # Darstellung
    # =========================================================

    def asString(self, mit_vz=True):

        if self.zaehler == 0:
            return "0"

        out = ""

        if self.is_neg() and mit_vz:
            out += "-"

        if self.nenner == 1:
            out += str(abs(self.zaehler))
        else:
            out += str(abs(self.zaehler)) + "/" + str(self.nenner)

        return out

    def asLatexString(self, mit_vz=True):

        if self.zaehler == 0:
            return "0"

        out = ""

        if self.is_neg() and mit_vz:
            out += "-"

        if self.nenner == 1:
            out += str(abs(self.zaehler))
        else:
            out += (
                r"\frac{"
                + str(abs(self.zaehler))
                + "}{"
                + str(self.nenner)
                + "}"
            )

        return out

    # =========================================================
    # Mathematik
    # =========================================================

    def plusQZahl(self, qzahl):

        zaehler = (
            self.zaehler * qzahl.nenner
            + qzahl.zaehler * self.nenner
        )

        nenner = self.nenner * qzahl.nenner

        self.set(zaehler, nenner)

    def minusQZahl(self, qzahl):

        zaehler = (
            self.zaehler * qzahl.nenner
            - qzahl.zaehler * self.nenner
        )

        nenner = self.nenner * qzahl.nenner

        self.set(zaehler, nenner)

    def prodOfQZahlen(self, q1, q2):

        zaehler = q1.zaehler * q2.zaehler
        nenner = q1.nenner * q2.nenner

        self.set(zaehler, nenner)

    def quotOfQZahlen(self, q1, q2):

        zaehler = q1.zaehler * q2.nenner
        nenner = q2.zaehler * q1.nenner

        self.set(zaehler, nenner)

    def diffOfQZahlen(self, q1, q2):

        zaehler = (
            q1.zaehler * q2.nenner
            - q2.zaehler * q1.nenner
        )

        nenner = q1.nenner * q2.nenner

        self.set(zaehler, nenner)

    # =========================================================
    # Kürzen
    # =========================================================

    def erweitereMit(self, zahl):

        if zahl is None:
            return

        self.zaehler *= zahl
        self.nenner *= zahl

    def kuerzbarQ(self):

        for i in range(2, 11):

            if (
                self.zaehler % i == 0
                and self.nenner % i == 0
            ):
                return i

        return 0

    def kuerzeMit(self, zahl):

        self.zaehler = int(self.zaehler / zahl)
        self.nenner = int(self.nenner / zahl)

    def kuerzeVoll(self):

        k = self.kuerzbarQ()

        while k != 0:
            self.kuerzeMit(k)
            k = self.kuerzbarQ()

    # =========================================================
    # Normalisierung
    # =========================================================

    def transform(self):

        if self.nenner == 0:
            raise ZeroDivisionError("Nenner darf nicht 0 sein")

        if self.zaehler < 0 and self.nenner < 0:
            self.zaehler = abs(self.zaehler)
            self.nenner = abs(self.nenner)

        elif self.zaehler > 0 and self.nenner < 0:
            self.zaehler = -self.zaehler
            self.nenner = abs(self.nenner)

        self.kuerzeVoll()

    # =========================================================
    # Vergleich
    # =========================================================

    def isEqualTo(self, qZahl):

        return (
            self.zaehler == qZahl.zaehler
            and self.nenner == qZahl.nenner
        )

class Term:
  def __init__(self, coeffs=[QZahl(0), QZahl(0)]):
    self.coeffs = coeffs
    self.latex_fig = None

  def asString(self, as_latex=False):
    out = ""
    temp = ""
    exp = len(self.coeffs) - 1
    is_first = True  # zählt bis zum ersten Koeffizient, der nicht Null ist

    for q in self.coeffs:

      # Die ersten Einträge mit Koeffizient Null werden übersprungen
      if q.asString() == "0":
        exp -= 1
        #i += 1
        continue

      # Koeffizient formatieren
      if as_latex:
        temp = q.asLatexString(mit_vz=False)
      else:
        temp = q.asString(mit_vz=False)
      if exp > 0 and (q.asString() == "1" or q.asString() == "-1"):
        temp = ""

      # Rechenzeichen formatieren
      if not is_first and q.is_neg():
        out += " - " + temp
      if not is_first and not q.is_neg():
        out += " + " + temp

      # Vorzeichen formatieren
      if is_first and q.is_neg():
        out += "-" + temp
        is_first = False
      if is_first and not q.is_neg():
        out += temp
        is_first = False

      # Variablen formatieren
      if exp > 0:
        out += "x"
      if exp > 1:
        out += "^" + str(exp)

      exp -= 1

    if out == "":
      return "0"
    return out

  def asLatexString(self):
    return self.asString(as_latex=True)

  def asLatexFig(self):
    out = self.asString(as_latex=True)
    # Länge bestimmen
    length = len(out) - out.count("frac")*10
    #print(length)
    # Bild erstellen mit variabler Länge
    self.latex_fig, self.ax = plt.subplots(figsize=(length*0.15, 0.4), dpi=400)
    formel = r"$" + out + r"$"
    self.ax.text(0, 0.5, formel, fontsize=14, verticalalignment="center") # transform=IdentityTransform()
    self.ax.set_axis_off()
    self.latex_fig.tight_layout()
    return self.latex_fig

  def closeLatexFig(self):
    if self.latex_fig:
      plt.close(self.latex_fig)


  def multByQZahl(self, q):
    for co in self.coeffs:
      co.prodOfQZahlen(co, q)

  def divideByQZahl(self, q):
    for co in self.coeffs:
      co.quotOfQZahlen(co, q)

  def plusQwithExp(self, q, exp):
    self.coeffs[len(self.coeffs)-1-exp].plusQZahl(q)

  def plusLinTerm(self, lin):
    for i in range(2):
      self.coeffs[i].plusQZahl(lin.coeffs[i])

  def minusLinTerm(self, lin):
    for i in range(2):
      self.coeffs[i].minusQZahl(lin.coeffs[i])

  def minusQwithExp(self, q, exp):
    self.coeffs[len(self.coeffs)-1-exp].minusQZahl(q)


class LinTerm(Term):
  def __init__(self, a=None, b=None):
    if not a:
      a = QZahl(0)
    if not b:
      b = QZahl(0)
    self.coeffs = [a, b]

  def fromString(self, string):         # gibt Fehlermeldung als string zurück

    errorQ = ""
    string = string.replace(" ", "")

    if string == "":
      return "Kein Eingabe"

    if string.find("x") == -1:              # Fall kein x enthalten:
      self.coeffs[0].fromString("0")                # Steigung = 0 setzen
      errorQ = self.coeffs[1].fromString(string)    # yA einlesen und nach Fehler fragen
      if errorQ:
        return errorQ
      return None

    string1, string2 = string.split("x", 1)
    if string1 == "":
      self.coeffs[0].fromString("1")
    elif string1 ==  "-":
      self.coeffs[0].fromString("-1")
    else:
      errorQ = self.coeffs[0].fromString(string1)    # m einlesen und nach Fehler fragen
      if errorQ:
        return errorQ
    if string2 == "":
      self.coeffs[1].fromString("0")
    else:
      errorQ = self.coeffs[1].fromString(string2)    # m einlesen und nach Fehler fragen
      if errorQ != "":
        return errorQ
    return None

  def fromLatexString(self, string):         # gibt Fehlermeldung als string zurück

    errorQ = ""
    string = string.replace(" ", "")

    if string == "":
      return "Kein Eingabe"

    if string.find("x") == -1:              # Fall kein x enthalten:
      self.coeffs[0].fromString("0")                # Steigung = 0 setzen
      errorQ = self.coeffs[1].fromLatexString(string)    # yA einlesen und nach Fehler fragen
      if errorQ:
        return errorQ
      return None

    string1, string2 = string.split("x", 1)
    if string1 == "":
      self.coeffs[0].fromString("1")
    elif string1 ==  "-":
      self.coeffs[0].fromString("-1")
    else:
      errorQ = self.coeffs[0].fromLatexString(string1)    # m einlesen und nach Fehler fragen
      if errorQ:
        return errorQ
    if string2 == "":
      self.coeffs[1].fromString("0")
    else:
      errorQ = self.coeffs[1].fromLatexString(string2)    # m einlesen und nach Fehler fragen
      if errorQ != "":
        return errorQ
    return None

  def asQ(self):
    if not self.coeffs[0].is_zero():
      return self.asString() + " ist keine Zahl"
    return self.coeffs[1]

class Equation():
  def __init__(self, term1=Term(), term2=Term()):
    self.term1 = term1
    self.term2 = term2

  def asString(self):
    return self.term1.asString() + " = " + self.term2.asString()

  def asLatexString(self):
    return self.term1.asLatexString() + " = " + self.term2.asLatexString()

  def bm_plusLinTerm(self, lin):
    for t in [self.term1, self.term2]:
      t.plusLinTerm(lin)

  def bm_minusLinTerm(self, lin):
    for t in [self.term1, self.term2]:
      t.minusLinTerm(lin)

  def bm_plusQwithExp(self, q, exp): # bm = balance methode
    for t in [self.term1, self.term2]:
      t.plusQwithExp(q, exp)


  def bm_minusQwithExp(self, q, exp):
    for t in [self.term1, self.term2]:
      t.minusQwithExp(q, exp)

  def bm_multByQ(self, q):
    for t in [self.term1, self.term2]:
      t.multByQZahl(q)

  def bm_divideByQ(self, q):
    for t in [self.term1, self.term2]:
      t.divideByQZahl(q)

  def asLatexFig(self):
    out = self.asLatexString()
    # Länge bestimmen
    length = len(out) - out.count("frac")*10
    #print(length)
    # Bild erstellen mit variabler Länge
    self.latex_fig = plt.figure(figsize=(length*0.15, 0.4), dpi=400)
    self.ax = self.latex_fig.add_axes([0,0,1,1])
    formel = r"$" + out + r"$"
    self.ax.text(0, 0.5, formel, fontsize=14, verticalalignment="center") # transform=IdentityTransform()
    self.ax.set_axis_off()
    #self.latex_fig.tight_layout()
    #self.latex_fig.savefig('image.png', bbox_inches='tight', pad_inches=0)
    return self.latex_fig

  def closeLatexFig(self):
    if self.latex_fig:
      plt.close(self.latex_fig)

class LinEquation(Equation):
  def __init__(self, lin1=LinTerm(), lin2=LinTerm()):
    while lin1.coeffs[0].asString() == "0" and len(lin1.coeffs) > 2:
      del lin1.coeffs[0]
      #print("geloescht")
    if len(lin1.coeffs) > 2:
      pass
      #print(lin1.asString() + "ist nicht linear")
    self.term1 = lin1
    self.term2 = lin2

  def fromString(self, string):
    errorQ = ""
    string = string.replace(" ", "")

    if string == "":
      return "Kein Eingabe"

    if string.find("=") == -1:              # Fall kein x enthalten:
      return "Gleichheitszeichnen fehlt"

    string1, string2 = string.split("=", 1)
    #print(string1 + ", " + string2)
    errorQ = self.term1.fromString(string1)    # m einlesen und nach Fehler fragen
    if errorQ:
      return errorQ
    errorQ = self.term2.fromString(string2)    # m einlesen und nach Fehler fragen
    if errorQ:
      return errorQ
    return None

  def get_m1(self):
    return self.term1.coeffs[0]

  def get_m2(self):
    return self.term2.coeffs[0]

  def get_c1(self):
    return self.term1.coeffs[1]

  def get_c2(self):
    return self.term2.coeffs[1]

  def next_step_to_solveQ(self):
    if not self.get_m1().is_zero() and not self.get_c1().is_zero():
      return [QZahl(self.get_c1().zaehler, self.get_c1().nenner), 0] # rechter Term mit Exp 1 wird sbtrahiert
    if self.get_m1().is_zero() and not self.get_c2().is_zero():
      return [QZahl(self.get_c2().zaehler, self.get_c2().nenner), 0] # linker Term mit Exp 1 wird sbtrahiert
    if self.get_c1().is_zero() and not self.get_m2().is_zero():
      return [QZahl(self.get_m2().zaehler, self.get_m2().nenner), 1] # linker Term mit Exp 0 wird subtrahiert

    if not self.get_m1().is_zero() and not self.get_m1().asString() == "1":
      return [QZahl(self.get_m1().zaehler, self.get_m1().nenner), -1] #durch m1 teilen
    if not self.get_m2().is_zero() and not self.get_m2().asString() == "1":
      return [QZahl(self.get_m2().zaehler, self.get_m2().nenner), -1] #durch m1 teilen
    return [None, None]

  def solve_completely(self):
    q, exp = self.next_step_to_solveQ()
    while q:
      if exp >= 0:
        #print("|-" + q.asString())
        self.bm_minusQwithExp(q, exp)
      if exp == -1:
        #print("|:" + q.asString())
        self.bm_divideByQ(q)
      q, exp = self.next_step_to_solveQ()
    #print(self.asString())

def create_bf_fig(vz, lin_term): # bf = balance_formation
  out = "| " + vz + " " + lin_term.asLatexString()
  # Länge bestimmen
  length = len(out) - out.count("frac")*10
  # Bild erstellen mit variabler Länge
  latex_fig = plt.figure(figsize=(length*0.15, 0.4), dpi=400)
  formel = r"$" + out + r"$"
  ax = latex_fig.add_axes([0,0,1,1])
  ax.text(0, 0.5, formel, fontsize=14, verticalalignment="center") # transform=IdentityTransform()
  ax.set_axis_off()
  return latex_fig




@dataclass
class Gerade:

    m: QZahl = field(default_factory=QZahl)
    c: QZahl = field(default_factory=QZahl)

    latex_fig: any = None

    # =========================================================
    # Konstruktion
    # =========================================================

    def fromLinTerm(self, lin):

        self.m = lin.coeffs[0]
        self.c = lin.coeffs[1]

    def fromPoints(self, p1, p2):

        if p1.x.isEqualTo(p2.x):
            return "Senkrechte Gerade nicht unterstützt"

        # dy = y2 - y1
        dy = QZahl()
        dy.diffOfQZahlen(p2.y, p1.y)

        # dx = x2 - x1
        dx = QZahl()
        dx.diffOfQZahlen(p2.x, p1.x)

        # m = dy / dx
        self.m.quotOfQZahlen(dy, dx)

        # c = y1 - m*x1
        mx = QZahl()
        mx.prodOfQZahlen(self.m, p1.x)

        self.c.diffOfQZahlen(p1.y, mx)

        return None

    def fromString(self, string):

        errorQ = ""

        string = string.replace(" ", "")

        # -----------------------------------------------------
        # Prüfen auf y=
        # -----------------------------------------------------

        if not string.startswith("y="):
            return "Eingabe muss beginnen mit: y = ..."

        string = string.split("y=")[1]

        if string == "":
            return "Kein Funktionsterm"

        # -----------------------------------------------------
        # Fall ohne x
        # -----------------------------------------------------

        if "x" not in string:

            self.m.fromString("0")

            errorQ = self.c.fromString(string)

            if errorQ:
                return errorQ

            return None

        # -----------------------------------------------------
        # Fall mit x
        # -----------------------------------------------------

        string1, string2 = string.split("x", 1)

        # Steigung
        if string1 == "":
            self.m.fromString("1")

        elif string1 == "-":
            self.m.fromString("-1")

        else:

            errorQ = self.m.fromString(string1)

            if errorQ:
                return errorQ

        # y-Achsenabschnitt
        if string2 == "":
            self.c.fromString("0")

        else:

            errorQ = self.c.fromString(string2)

            if errorQ:
                return errorQ

        return None

    # =========================================================
    # Darstellung
    # =========================================================

    def _format(self, latex=False):

        # -----------------------------------------------------
        # Steigung formatieren
        # -----------------------------------------------------

        m_str = self.m.asString()

        if m_str == "0":

            if latex:
                return "y = " + self.c.asLatexString()

            return "y = " + self.c.asString()

        # m-Ausgabe
        if m_str == "1":
            m_out = ""

        elif m_str == "-1":
            m_out = "-"

        else:

            if latex:
                m_out = self.m.asLatexString()
            else:
                m_out = self.m.asString()

        # -----------------------------------------------------
        # y-Achsenabschnitt formatieren
        # -----------------------------------------------------

        c_str = self.c.asString(mit_vz=False)

        c_out = ""

        if c_str == "0":
            pass

        elif self.c.is_neg():

            if latex:
                c_out = " - " + self.c.asLatexString(mit_vz=False)
            else:
                c_out = " - " + c_str

        else:

            if latex:
                c_out = " + " + self.c.asLatexString()
            else:
                c_out = " + " + c_str

        return "y = " + m_out + "x" + c_out

    def asQString(self):
        return self._format(latex=False)

    def asLatexString(self):
        return self._format(latex=True)

    def asString(self):
        return self.asQString()

    # =========================================================
    # Vergleich
    # =========================================================

    def is_equal_to(self, other):

        if not isinstance(other, Gerade):
            return False

        return (
            self.m.isEqualTo(other.m)
            and self.c.isEqualTo(other.c)
        )

    def diagnose_gerade(self, soll):

        if self == soll:
            return "✅ Die Gerade ist korrekt."

        meldungen = []
    
        # =====================================================
        # Prüffunktionen
        # =====================================================
    
        def check_steigung():
    
            if not self.m.isEqualTo(soll.m):
    
                meldungen.append(
                    "Die Steigung stimmt nicht."
                )
    
        def check_y_achsenabschnitt():
    
            if not self.c.isEqualTo(soll.c):
    
                meldungen.append(
                    "Der y-Achsenabschnitt stimmt nicht."
                )
    
        def check_vorzeichenfehler():
    
            neg_m = QZahl(
                -soll.m.zaehler,
                soll.m.nenner
            )
    
            if self.m.isEqualTo(neg_m):
    
                meldungen.append(
                    "Die Steigung hat das falsche Vorzeichen."
                )
    
        def check_kehrwertfehler():
    
            if soll.m.zaehler == 0:
                return
    
            if (
                self.m.zaehler == soll.m.nenner
                and self.m.nenner == soll.m.zaehler
            ):
    
                meldungen.append(
                    "Die Steigung wurde vermutlich vertauscht "
                    "(Δx und Δy verwechselt)."
                )
    
        def check_steigung_vergessen():
    
            if (
                self.m.is_zero()
                and not soll.m.is_zero()
            ):
    
                meldungen.append(
                    "Die Steigung fehlt."
                )
    
        def check_y_abschnitt_vergessen():
    
            if (
                self.c.is_zero()
                and not soll.c.is_zero()
            ):
    
                meldungen.append(
                    "Der y-Achsenabschnitt fehlt."
                )
    
        # =====================================================
        # Prüfungen ausführen
        # =====================================================
    
        check_steigung()
    
        check_y_achsenabschnitt()
    
        check_vorzeichenfehler()
    
        check_kehrwertfehler()
    
        check_steigung_vergessen()
    
        check_y_abschnitt_vergessen()
    
        # =====================================================
        # Ergebnis
        # =====================================================

        if len(meldungen) == 0:
    
            return "✅ "
    
        out = "❌ "
        for meldung in meldungen:
            out += meldung + " "
        return out

    # =========================================================
    # Plotten
    # =========================================================

    def plotToCS(self, cs, color):

        x = np.arange(-5, 5, 0.01)

        y = (
            self.m.asFloat() * x
            + self.c.asFloat()
        )

        cs.ax.plot(
            x,
            y,
            color=color,
            linewidth=1.2
        )

    # =========================================================
    # Latex
    # =========================================================

    def asLatexFig(self):

        self.latex_fig, ax = plt.subplots(
            figsize=(2, 0.4),
            dpi=400
        )

        formel = r"$" + self.asLatexString() + r"$"

        ax.text(
            0,
            0.5,
            formel,
            fontsize=14,
            verticalalignment="center"
        )

        ax.set_axis_off()

        self.latex_fig.tight_layout()

        return self.latex_fig

    def closeLatexFig(self):

        if self.latex_fig:
            plt.close(self.latex_fig)



class Point:
  def __init__(self, x=QZahl(0), y=QZahl(1)):
    self.x = x
    self.y = y

  def increase_y_by(self, qzahl):
    self.y.plusQZahl(qzahl)

  def increase_x_by(self, qzahl):
    self.x.plusQZahl(qzahl)

  def plotToCS(self, cs):
    cs.ax.plot(self.x.asFloat(), self.y.asFloat(), marker="o")

  def asString(self):
    return "(" + self.x.asString() + "|" + self.y.asString() + ")"



class CoordSys:
  def __init__(self):
    self.fig, self.ax = plt.subplots(figsize=(3.5,3.5), dpi=400) # , dpi=500
    #fig.set_size_inches((4, 4))
    #fig.set_dpi(500)

    plt.rcParams.update({"font.size": 7})
    plt.rcParams.update({"mathtext.fontset": "dejavusans"})
    plt.rcParams.update({"font.family": "monospace"})
    #plt.rcParams.update({'xtick.color': "grey"})
    #plt.rcParams.update({'ytick.color': "grey"})

    #fig.set_frameon(False)
    #plt.title(r"$\alpha$")

    # Reichweite der Achsen
    plt.xlim([-3.1,3.1])
    plt.ylim([-3.1,3.1])

    # Grid einrichten
    plt.gca().xaxis.set_major_locator(MultipleLocator(1))
    plt.gca().xaxis.set_minor_locator(MultipleLocator(0.5))
    plt.gca().yaxis.set_major_locator(MultipleLocator(1))
    plt.gca().yaxis.set_minor_locator(MultipleLocator(0.5))
    plt.grid(True, "major", color="lightgrey")
    plt.grid(True, "minor", color="lightgrey")

    #Achsen setzen
    self.ax.spines["right"].set_color("none")
    self.ax.spines["top"].set_color("none")
    self.ax.spines["left"].set_position(("data", 0))
    self.ax.spines["bottom"].set_position(("data", 0))

    self.fig.tight_layout()

  def get_fig(self):
    return self.fig

  def clear(self):
    for el in self.ax.get_lines():
      el.remove()

class EditableFormula:
  def __init__(self):
    #self.elements = []
    self.cursor_sign = r"\blacksquare"
    self.latex_string = ""
    self.form_string = ""
    self.pos = 0
    self.form_string = "¢ "
    self.fig = None
    self.editableQ = True

  def set_editable(self, edQ):
      if edQ == True:
          self.editableQ = True
      elif edQ == False:
          self.editableQ = False
      else:
          return None

  def get_fig(self):
    if self.fig:
      plt.close(self.fig)
    length = len(self.form_string) - self.form_string.count("frac")*10 - 11
    self.fig = plt.figure(figsize=(2, 0.4), dpi=400)
    self.ax = self.fig.add_axes([0,0,1,1])
    if self.editableQ:
        latex_string = r"$" + self.form_string.replace("¢", self.cursor_sign) + r"$"
    else:
        latex_string = r"$" + self.form_string.replace("¢", "") + r"$"
    self.ax.text(0, 0.45, latex_string, color="#37474F", fontsize=14, weight="ultralight", verticalalignment="center") # transform=IdentityTransform()
    self.ax.set_axis_off()
    return self.fig

  def insert(self, string):
    if not self.editableQ:
        return None
    string1, string2 = self.form_string.split("¢ ")
    self.form_string = string1 + " " + string + "¢ " + string2
    #print(self.form_string)
    #self.get_fig()
    #plt.show()

  def insert_frac(self):
    if not self.editableQ:
        return None
    string1, string2 = self.form_string.split("¢ ")
    self.form_string = string1 + " " + r"\frac{\,¢ \,}{\, \,} " + string2
    #print(self.form_string)

  def move_left(self):
    if not self.editableQ:
        return None
    string1, string2 = self.form_string.split("¢")
    index = len(string1) - 1
    if index < 0:
      return None
    while not string1[index] == " ":
      index -= 1
    copied_string1 = ""
    copied_string2 = ""
    i = 0
    while i < index:
      copied_string1 += string1[i]
      i += 1
    while i < len(string1):
      copied_string2 += string1[i]
      i += 1
    self.form_string = copied_string1 + "¢" + copied_string2 + string2
    #print(self.form_string)

  def move_right(self):
    if not self.editableQ:
        return None
    string1, string2 = self.form_string.split("¢")
    if string2 == " ":
      return None
    copied_string1 = " "
    copied_string2 = ""
    i = 1
    while not string2[i] == " ":
      copied_string1 += string2[i]
      i += 1
    while i < len(string2):
      copied_string2 += string2[i]
      i += 1
    self.form_string = string1 + copied_string1 + "¢" + copied_string2
    #print(self.form_string)

  def delete_last(self): #der string bis zum vorherigen Leerzeichen wird kopiert und untersucht
    if not self.editableQ:
        return None
    string1, string2 = self.form_string.split("¢ ")
    index = len(string1)-1
    if index < 0:
      return None
    copied_string = ""
    while string1[index] != " ":
      copied_string += string1[index]
      index -= 1
    #print("Kopiert: " + copied_string)
    if copied_string.find(r"},") != -1: # ..\,}... rückwärts
      self.move_left()
      #print("nur nach links gegangen")
      #print(self.form_string)
      return None
    if copied_string.find("carf") != -1: # ..frac... rückwärts
      copied_string = ""
      bracket_count = 0
      while bracket_count < 4:
        char = self.form_string[index]
        copied_string += char
        if char == "{" or char == "}":
          bracket_count += 1
        index += 1
      #print("Kopierter Bruch: " + copied_string)
      string1, string2 = self.form_string.split(copied_string)
      self.form_string = string1 + "¢" + string2
      print(self.form_string)
      return None
    split_string = " " + copied_string + "¢ "
    string1, string2 = self.form_string.split(split_string)
    self.form_string = string1 + "¢ " + string2
    #print(self.form_string)

  def clear(self):
    if not self.editableQ:
        return None
    self.form_string = "¢ "

  def get_string(self):
    return self.form_string.replace("¢", "")

#cs = CoordSys()
# p = Point(QZahl(2), QZahl(1, 2))
# p.plotToCS(cs)
#g = Gerade()
#g.fromString("y=-0,5x+2")
#g.plotToCS(cs, "blue")
#g.asLatexString()

# cs.clear()

# g.plotToCS(cs)

#form = EditableFormula()
