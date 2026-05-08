from scipy.optimize import linprog


def resoudre(couts, nutrition, besoins):
    """
    Résout le problème de programmation linéaire.

    Paramètres :
    - couts      : liste de 3 coûts [c1, c2, c3]
    - nutrition  : matrice 3x3 des apports nutritionnels [[a11, a12, a13], ...]
    - besoins    : liste de 3 besoins minimaux [b1, b2, b3]

    Retourne un dictionnaire avec :
    - 'quantites' : liste [x1, x2, x3]
    - 'cout_total' : coût minimal
    - 'succes'    : True si solution trouvée
    - 'message'   : message d'état
    """

    # scipy minimise, on veut minimiser c1*x1 + c2*x2 + c3*x3
    c = couts

    # Les contraintes sont : nutrition * x >= besoins
    # scipy gère uniquement <=, donc on multiplie par -1 : -nutrition * x <= -besoins
    A_ub = [[-nutrition[i][j] for j in range(3)] for i in range(3)]
    b_ub = [-besoins[i] for i in range(3)]

    # Les variables doivent être >= 0
    bornes = [(0, None), (0, None), (0, None)]

    # Résolution
    resultat = linprog(
        c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bornes,
        method='highs'
    )

    if resultat.success:
        return {
            'succes': True,
            'quantites': [round(x, 4) for x in resultat.x],
            'cout_total': round(resultat.fun, 4),
            'message': 'Solution optimale trouvée.'
        }
    else:
        return {
            'succes': False,
            'quantites': [0, 0, 0],
            'cout_total': 0,
            'message': 'Aucune solution réalisable. Vérifiez vos données.'
        }


# ==============================
# TEST AVEC LES VALEURS DU RAPPORT
# ==============================
if __name__ == "__main__":
    couts     = [4, 6, 5]
    nutrition = [
        [3, 4, 2],   # contrainte 1 (ex: protéines)
        [1, 3, 2],   # contrainte 2 (ex: lipides)
        [2, 1, 4]    # contrainte 3 (ex: glucides)
    ]
    besoins   = [60, 40, 50]

    resultat = resoudre(couts, nutrition, besoins)

    print("=" * 40)
    print("   RÉSULTAT DE L'OPTIMISATION")
    print("=" * 40)
    if resultat['succes']:
        q = resultat['quantites']
        print(f"  x1 = {q[0]}")
        print(f"  x2 = {q[1]}")
        print(f"  x3 = {q[2]}")
        print(f"  Coût minimal = {resultat['cout_total']} dh")
    else:
        print(f"  Erreur : {resultat['message']}")
    print("=" * 40)