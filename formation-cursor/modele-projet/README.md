# Modèle à copier dans un repo de travail

À la racine de CathQ, HPP, ERP, Vitizen (ou un repo pro) :

```bash
cp -r formation-cursor/modele-projet/.cursor /chemin/vers/ton-repo/
```

Puis édite `.cursor/rules/02-contexte-projet.mdc` (nom, commandes de test,
chemins data). Sans ce fichier, Cursor redécouvre le projet à chaque chat
et propose trop large.
