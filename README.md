# Finance Board

## Bond Analyzer

Finance Board est une application Streamlit dédiée à l’analyse d’obligations.  
Elle permet de saisir les principales caractéristiques d’une obligation et d’obtenir une première analyse de ses flux financiers et de ses indicateurs de risque.

Le projet est actuellement en cours de développement.

---

## Présentation

Cette application constitue une refonte d’un ancien projet personnel d’analyse financière.

L’objectif de cette nouvelle version est de repartir sur une base plus claire, plus structurée et plus interactive, en utilisant Streamlit pour construire une interface simple et accessible depuis un navigateur.

La première version se concentre sur l’analyse individuelle d’une obligation.

---

## Fonctionnalités actuelles

L’application permet de renseigner :

- l’ISIN ;
- le nom de l’obligation ;
- l’émetteur ;
- le nominal ;
- le taux du coupon ;
- le yield to maturity ;
- la date d’émission ;
- la date de maturité ;
- la fréquence de paiement du coupon.

À partir de ces informations, l’application génère :

- l’échéancier des cash flows ;
- les paiements de coupons ;
- le remboursement du nominal à maturité ;
- la distinction entre flux passés et flux futurs ;
- la duration ;
- la modified duration ;
- le DV01.

Les flux passés sont affichés différemment des flux futurs afin de rendre l’échéancier plus lisible.

---

## Technologies utilisées

- Python
- Streamlit
- Pandas
- HTML / CSS pour la personnalisation de l’interface
- GitHub Codespaces pour le développement
- Streamlit Community Cloud pour le déploiement

---

## Structure actuelle du projet

```text
Finance_Board/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── .devcontainer/
    └── devcontainer.json