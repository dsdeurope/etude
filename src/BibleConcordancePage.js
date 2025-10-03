import React, { useState, useEffect } from 'react';
import ThemeVersesPage from './ThemeVersesPage';

const BibleConcordancePage = ({ onGoBack }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Nouvel état pour la recherche de personnages
  const [characterSearchTerm, setCharacterSearchTerm] = useState("");
  const [characterResults, setCharacterResults] = useState([]);
  const [isCharacterLoading, setIsCharacterLoading] = useState(false);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [characterHistory, setCharacterHistory] = useState("");
  const [activeTab, setActiveTab] = useState("concordance"); // "concordance" ou "characters"

  // Liste des personnages bibliques principaux
  const biblicalCharacters = [
    // Ancien Testament
    "Abraham", "Isaac", "Jacob", "Moïse", "David", "Salomon", "Noé", "Adam", "Ève", 
    "Caïn", "Abel", "Énoch", "Mathusalem", "Joseph", "Benjamin", "Juda", "Lévi",
    "Aaron", "Josué", "Samuel", "Saül", "Jonathan", "Goliath", "Ruth", "Naomi",
    "Booz", "Élie", "Élisée", "Jérémie", "Ésaïe", "Ézéchiel", "Daniel", "Jonas",
    "Job", "Esther", "Mardochée", "Aman", "Néhémie", "Esdras", "Zorobabel",
    "Gédéon", "Samson", "Dalila", "Déborah", "Barak", "Jephté", "Rahab",
    // Nouveau Testament
    "Jésus", "Marie", "Joseph", "Jean-Baptiste", "Pierre", "Paul", "Jean",
    "Jacques", "André", "Philippe", "Barthélemy", "Matthieu", "Thomas",
    "Jacques fils d'Alphée", "Simon le Zélote", "Jude", "Judas Iscariote",
    "Marie Madeleine", "Marthe", "Lazare", "Marie de Béthanie", "Nicodème",
    "Zachée", "Pilate", "Hérode", "Anne", "Caïphe", "Barnabas", "Timothée",
    "Tite", "Philémon", "Lydie", "Priscille", "Aquila", "Apollos", "Silas"
  ].sort();

  // Fonction pour générer l'histoire détaillée d'un personnage avec croisement de versets
  const generateCharacterHistory = async (character) => {
    setIsCharacterLoading(true);
    setSelectedCharacter(character);

    try {
      // Simuler un appel API pour générer l'histoire du personnage
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Prompt spécialisé pour générer l'histoire complète du personnage
      const prompt = `Génère l'histoire biblique complète de ${character} en croisant tous les versets bibliques le concernant. 

STRUCTURE REQUISE :
1. IDENTITÉ ET GÉNÉALOGIE
2. NAISSANCE ET JEUNESSE  
3. ÉVÉNEMENTS MAJEURS DE SA VIE
4. SES RELATIONS FAMILIALES ET AMICALES
5. SES ŒUVRES ET ACCOMPLISSEMENTS
6. SES ÉPREUVES ET DÉFIS
7. SA FOI ET SA RELATION AVEC DIEU
8. SA MORT OU FIN DE VIE (si mentionnée)
9. SON HÉRITAGE ET POSTÉRITÉ
10. VERSETS-CLÉS À RETENIR

Croise tous les passages bibliques disponibles. Sois narratif, détaillé et historiquement précis selon les Écritures. Minimum 2000 mots.`;

      // Histoire générée (simulée pour la démo)
      const mockHistory = generateMockCharacterHistory(character);
      setCharacterHistory(mockHistory);

    } catch (error) {
      console.error("Erreur génération histoire:", error);
      setCharacterHistory("Erreur lors de la génération de l'histoire du personnage.");
    } finally {
      setIsCharacterLoading(false);
    }
  };

  // Fonction pour générer une histoire mock (en attendant l'intégration API)
  const generateMockCharacterHistory = (character) => {
    const histories = {
      "Abraham": `
        ## 🌟 ABRAHAM - Le Père de la Foi (vers 2000 av. J.-C.)

        ### 1. IDENTITÉ ET GÉNÉALOGIE
        Abraham, né Abram (signifiant "père élevé"), fils de Térach, descendant de Sem. Originaire d'Ur en Chaldée (actuel Irak). Sa généalogie remonte à Noé par Sem. Marié à Sara (d'abord appelée Saraï), sa demi-sœur par son père.

        ### 2. NAISSANCE ET JEUNESSE À UR
        Né vers 2166 av. J.-C. à Ur, grande cité mésopotamienne connue pour ses ziggourats et le culte des idoles. Térah, son père, était probablement marchand. Environnement païen où l'on adorait le dieu-lune Nanna.

        ### 3. L'APPEL DE DIEU ET LA GRANDE MIGRATION
        **Genèse 12:1-3** : "L'Éternel dit à Abram: Va-t'en de ton pays, de ta patrie, et de la maison de ton père, dans le pays que je te montrerai." À 75 ans, obéit à l'appel divin sans connaître sa destination. Première manifestation de sa foi exceptionnelle.

        **Étapes du voyage** :
        - Ur → Charan (avec Térach, mort à 205 ans)  
        - Charan → Canaan (avec Sara, Lot, serviteurs)
        - Première étape en Canaan : Sichem, chêne de Moré

        ### 4. LES ALLIANCES DIVINES
        **Première alliance (Genèse 12:2-3)** : Promesse d'une grande nation, bénédiction personnelle, bénédiction universelle.

        **Alliance renforcée (Genèse 15:5-6)** : "Regarde vers le ciel, et compte les étoiles... Ainsi sera ta postérité." Abraham crut et cela lui fut imputé à justice.

        **Alliance de la circoncision (Genèse 17:4-8)** : Changement de nom (Abram → Abraham, "père d'une multitude"), circoncision comme signe, promesse de la terre de Canaan.

        ### 5. ÉPREUVES DE FOI MAJEURES
        **La famine en Égypte (Genèse 12:10-20)** : Première grande épreuve, mensonge sur Sara, intervention divine pour la protéger.

        **Séparation d'avec Lot (Genèse 13)** : Conflits entre bergers, Abraham choisit la paix en laissant Lot choisir sa terre.

        **Guerre des rois (Genèse 14)** : Abraham guerrier libérant Lot, rencontre avec Melchisédek, refus des biens du roi de Sodome.

        **Le sacrifice d'Isaac (Genèse 22)** : Épreuve suprême de la foi. "Prends ton fils, ton unique, que tu aimes, Isaac..." Intervention de l'ange au dernier moment.

        ### 6. DESCENDANCE ET PROMESSES
        **Ismaël avec Agar** (Genèse 16) : Né quand Abraham avait 86 ans. Sara stérile pousse Abraham vers sa servante. Source de tensions familiales.

        **Isaac, fils de la promesse** (Genèse 21) : Né quand Abraham avait 100 ans et Sara 90 ans. Rire de Sara : "Dieu m'a fait un sujet de rire."

        ### 7. RELATIONS ET INTERCESSION
        **Intercession pour Sodome** (Genèse 18:22-33) : Dialogue extraordinaire avec Dieu, marchandage pour sauver la ville. Révèle son cœur compassionnel.

        **Relations avec les peuples locaux** : Alliances avec Abimélec, respect mutuel avec les Héthiens pour l'achat de la grotte de Macpéla.

        ### 8. MORT ET SÉPULTURE
        Mort à 175 ans (Genèse 25:7-8) : "Abraham expira et mourut dans une heureuse vieillesse, âgé et rassasié de jours." Enterré dans la grotte de Macpéla avec Sara par Isaac et Ismaël réconciliés.

        ### 9. HÉRITAGE SPIRITUEL
        **Père de trois religions monothéistes** : Judaïsme, Christianisme, Islam le vénèrent.

        **Modèle de foi** (Romains 4:16, Hébreux 11:8-12) : "C'est pourquoi les héritiers le sont par la foi, pour que ce soit par grâce."

        **Ami de Dieu** (Jacques 2:23, 2 Chroniques 20:7) : Titre unique dans les Écritures.

        ### 10. VERSETS-CLÉS À RETENIR
        - **Genèse 15:6** : "Abram crut à l'Éternel, qui le lui imputa à justice."
        - **Genèse 22:14** : "Abraham donna à ce lieu le nom de Jéhovah-Jiré."  
        - **Romains 4:17** : "Dieu qui donne la vie aux morts, et qui appelle les choses qui ne sont point comme si elles étaient."
        - **Galates 3:9** : "De sorte que ceux qui croient sont bénis avec Abraham le croyant."

        Abraham demeure le prototype du croyant qui obéit à Dieu par la foi, modèle éternel pour tous les âges.
      `,
      "Aaron": `
        ## AARON - Le Grand Prêtre d'Israël (vers 1393-1273 av. J.-C.)

        Aaron, dont le nom hébreu signifie "montagnard" ou "éclairé", naît vers 1396 av. J.-C. en Égypte sous l'oppression pharaonique. Fils d'Amram et de Jokébed de la tribu de Lévi, il grandit aux côtés de son frère cadet Moïse et de sa sœur Miriam dans une famille pieuse qui préserve la foi d'Abraham malgré l'esclavage. Son mariage avec Élischéba, fille d'Amminadab, lui donne quatre fils : Nadab, Abihu, Éléazar et Ithamar, qui marqueront l'histoire du sacerdoce d'Israël.

        L'appel divin transforme Aaron en porte-parole de Moïse. Selon **Exode 4:14-16**, l'Éternel déclare : "N'y a-t-il pas ton frère Aaron, le Lévite ? Je sais qu'il parlera facilement." Cette élection divine scelle le destin d'Aaron comme médiateur entre Dieu et son peuple. Leur première rencontre prophétique à la montagne de Dieu après quarante ans de séparation inaugure un ministère commun extraordinaire.

        Devant Pharaon, Aaron démontre la puissance divine en transformant son bâton en serpent qui dévore ceux des magiciens égyptiens. Il exécute plusieurs des dix plaies : l'eau changée en sang, les grenouilles et les moustiques, attestant ainsi la supériorité du Dieu d'Israël sur les divinités égyptiennes. Cette démonstration de force prépare la libération d'Israël de l'esclavage.

        Pendant l'Exode, Aaron guide avec Moïse plus de 600 000 hommes hors d'Égypte, participant aux grands miracles : le passage de la mer Rouge, l'eau jaillissant du rocher et la manne tombant du ciel. Lors de la bataille contre Amalek, Aaron soutient avec Hur les mains levées de Moïse, assurant ainsi la victoire d'Israël par la prière et l'intercession.

        L'institution divine de la prêtrise marque l'apogée de la vie d'Aaron. Selon **Exode 28:1**, Dieu ordonne : "Fais approcher de toi Aaron, ton frère, et ses fils avec lui, du milieu des enfants d'Israël, pour qu'ils soient à mon service dans le sacerdoce." Aaron revêt alors les vêtements sacrés : l'éphod, le pectoral orné de douze pierres précieuses représentant les tribus d'Israël, et la tiare portant l'inscription "Sainteté à l'Éternel". Sept jours de consécration, l'onction d'huile sainte et des sacrifices d'expiation établissent le sacerdoce aaronique pour l'éternité.

        Comme Grand Prêtre, Aaron assume des responsabilités uniques. Seul autorisé à pénétrer dans le Saint des Saints lors du Jour des Expiations, il offre l'expiation pour les péchés d'Israël. Ses journées se remplissent d'holocaustes perpétuels matin et soir, d'intercession constante pour le peuple. La bénédiction sacerdotale de **Nombres 6:24-26** résonne de sa bouche : "Que l'Éternel te bénisse, et qu'il te garde ! Que l'Éternel fasse luire sa face sur toi, et qu'il t'accorde sa grâce !"

        Cependant, Aaron n'échappe pas aux épreuves humaines. En l'absence de Moïse au Sinaï, il cède à la pression populaire et façonne le veau d'or, proclamant : "Voici ton dieu, Israël, qui t'a fait sortir d'Égypte !" Ce grave péché d'idolâtrie révèle sa vulnérabilité, mais l'intercession de Moïse lui obtient le pardon divin. Plus tard, la mort foudroyante de ses fils Nadab et Abihu, qui offrent un "feu étranger" devant l'Éternel, le plonge dans un silence douloureux mais soumis au jugement de Dieu.

        Sa rébellion avec Miriam contre Moïse concernant sa femme éthiopienne révèle également ses luttes fraternelles. Quand Miriam est frappée de lèpre, Aaron intercède pour sa sœur, manifestant son cœur compatissant. La révolte de Koré contre son autorité sacerdotale trouve sa réponse divine dans le miracle de la verge : seule celle d'Aaron fleurit et produit des amandes, confirmant son élection. Cette verge miraculeuse est conservée dans l'arche comme témoignage perpétuel.

        À 123 ans, Aaron gravit le mont Hor avec Moïse et son fils Éléazar. Dieu lui annonce sa mort imminente en châtiment de sa rébellion aux eaux de Meriba. Dans un geste solennel, Aaron transmet ses vêtements sacerdotaux à Éléazar qui lui succède, puis rend paisiblement son dernier souffle. "Toute la maison d'Israël pleura Aaron pendant trente jours," témoignage de l'amour du peuple pour son Grand Prêtre.

        L'héritage spirituel d'Aaron traverse les siècles. Sa lignée assure le sacerdoce jusqu'à l'époque de Jésus, préfigurant le Christ, notre Grand Souverain Sacrificateur selon **Hébreux 4:14-16**. Tandis qu'Aaron offrait des sacrifices répétés, Christ s'est offert une fois pour toutes. Aaron demeure le modèle du médiateur fidèle, intercédant malgré ses faiblesses humaines, annonçant le parfait sacerdoce du Messie qui réconcilie définitivement Dieu et les hommes.
      `
    };

    return histories[character] || `
      ## ${character} - Histoire Biblique Détaillée

      L'histoire complète de ${character} sera générée en croisant tous les passages bibliques le concernant. Cette fonctionnalité utilisera l'API Gemini pour créer un récit détaillé incluant :

      - Sa généalogie et origine
      - Les événements majeurs de sa vie
      - Ses relations avec Dieu et les hommes  
      - Son héritage spirituel
      - Les versets-clés le concernant

      *Génération en cours de développement...*
    `;
  };

  // Fonction Gemini pour enrichir la concordance de thèmes
  const handleGeminiConcordance = async () => {
    if (!searchTerm.trim()) {
      alert("Veuillez d'abord saisir un terme à rechercher");
      return;
    }
    
    setIsLoading(true);
    try {
      // Simuler appel API Gemini pour enrichir la concordance
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Générer plus de versets avec Gemini (simulé)
      const enrichedResults = [
        ...results,
        // Ajouter des versets enrichis par Gemini
        { book: "Proverbes", chapter: 8, verse: 17, text: `Les versets enrichis par Gemini pour "${searchTerm}" incluent des références croisées et des contextes approfondis...` },
        { book: "Psaume", chapter: 119, verse: 105, text: `Analyse théologique approfondie du terme "${searchTerm}" selon les commentaires bibliques et la tradition...` }
      ];
      
      setResults(enrichedResults);
      console.log(`[GEMINI CONCORDANCE] Enrichissement pour "${searchTerm}"`);
    } catch (error) {
      console.error("Erreur Gemini concordance:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fonction Gemini pour enrichir l'histoire des personnages
  const handleGeminiCharacter = async () => {
    if (!selectedCharacter) {
      alert("Veuillez d'abord sélectionner un personnage biblique");
      return;
    }
    
    setIsCharacterLoading(true);
    try {
      // Simuler appel API Gemini pour enrichir l'histoire du personnage
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const enrichedHistory = `
${characterHistory}

## 🤖 ENRICHISSEMENT GEMINI

### ANALYSE THÉOLOGIQUE APPROFONDIE
L'intelligence artificielle Gemini a analysé ${selectedCharacter} en croisant tous les passages bibliques et apporte ces éclairages supplémentaires :

- **Contexte historique enrichi** : Analyse des sources extra-bibliques
- **Typologie christologique** : Préfigurations du Christ dans la vie de ${selectedCharacter}
- **Applications contemporaines** : Leçons pour le croyant d'aujourd'hui
- **Références croisées** : Liens avec d'autres personnages bibliques

*Enrichissement généré par Gemini AI pour une compréhension plus profonde des Écritures.*
      `;
      
      setCharacterHistory(enrichedHistory);
      console.log(`[GEMINI PERSONNAGE] Enrichissement pour ${selectedCharacter}`);
    } catch (error) {
      console.error("Erreur Gemini personnage:", error);
    } finally {
      setIsCharacterLoading(false);
    }
  };

  const generateConcordanceResults = (term) => {
    const mockVerses = {
      "amour": [
        { book: "Jean", chapter: 3, verse: 16, text: "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle." },
        { book: "1 Corinthiens", chapter: 13, verse: 4, text: "L'amour est patient, il est plein de bonté; l'amour n'est point envieux; l'amour ne se vante point, il ne s'enfle point d'orgueil," },
        { book: "1 Jean", chapter: 4, verse: 8, text: "Celui qui n'aime pas n'a pas connu Dieu, car Dieu est amour." },
        { book: "1 Jean", chapter: 4, verse: 19, text: "Pour nous, nous l'aimons, parce qu'il nous a aimés le premier." },
        { book: "Romains", chapter: 8, verse: 38, text: "Car j'ai l'assurance que ni la mort ni la vie, ni les anges ni les dominations, ni les choses présentes ni les choses à venir, ni les puissances, ni la hauteur, ni la profondeur, ni aucune autre créature ne pourra nous séparer de l'amour de Dieu manifesté en Jésus-Christ notre Seigneur." },
        { book: "1 Corinthiens", chapter: 13, verse: 13, text: "Maintenant donc ces trois choses demeurent: la foi, l'espérance, la charité; mais la plus grande de ces choses, c'est la charité." },
        { book: "Éphésiens", chapter: 3, verse: 19, text: "et connaître l'amour de Christ, qui surpasse toute connaissance, en sorte que vous soyez remplis jusqu'à toute la plénitude de Dieu." }
      ],
      "paix": [
        { book: "Jean", chapter: 14, verse: 27, text: "Je vous laisse la paix, je vous donne ma paix. Je ne vous donne pas comme le monde donne. Que votre cœur ne se trouble point, et ne s'alarme point." },
        { book: "Philippiens", chapter: 4, verse: 7, text: "Et la paix de Dieu, qui surpasse toute intelligence, gardera vos cœurs et vos pensées en Jésus-Christ." },
        { book: "Ésaïe", chapter: 26, verse: 3, text: "A celui qui est ferme dans ses sentiments Tu assures la paix, la paix, Parce qu'il se confie en toi." },
        { book: "Romains", chapter: 5, verse: 1, text: "Étant donc justifiés par la foi, nous avons la paix avec Dieu par notre Seigneur Jésus-Christ." },
        { book: "Jean", chapter: 16, verse: 33, text: "Je vous ai dit ces choses, afin que vous ayez la paix en moi. Vous aurez des tribulations dans le monde; mais prenez courage, j'ai vaincu le monde." }
      ],
      "foi": [
        { book: "Hébreux", chapter: 11, verse: 1, text: "Or la foi est une ferme assurance des choses qu'on espère, une démonstration de celles qu'on ne voit point." },
        { book: "Romains", chapter: 10, verse: 17, text: "Ainsi la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ." },
        { book: "Éphésiens", chapter: 2, verse: 8, text: "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu." },
        { book: "Marc", chapter: 11, verse: 22, text: "Jésus prit la parole, et leur dit: Ayez foi en Dieu." },
        { book: "Habacuc", chapter: 2, verse: 4, text: "Voici, son âme s'est enflée, elle n'est pas droite en lui; Mais le juste vivra par sa foi." },
        { book: "Jacques", chapter: 2, verse: 17, text: "Il en est ainsi de la foi: si elle n'a pas les œuvres, elle est morte en elle-même." }
      ],
      "joie": [
        { book: "Néhémie", chapter: 8, verse: 10, text: "Il leur dit: Allez, mangez des viandes grasses et buvez des liqueurs douces, et envoyez des portions à ceux qui n'ont rien de préparé, car ce jour est consacré à notre Seigneur; ne vous affligez pas, car la joie de l'Éternel sera votre force." },
        { book: "Psaume", chapter: 16, verse: 11, text: "Tu me feras connaître le sentier de la vie; Il y a d'abondantes joies devant ta face, Des délices éternelles à ta droite." },
        { book: "Galates", chapter: 5, verse: 22, text: "Mais le fruit de l'Esprit, c'est l'amour, la joie, la paix, la patience, la bonté, la bénignité, la fidélité, la douceur, la tempérance;" },
        { book: "Jean", chapter: 15, verse: 11, text: "Je vous ai dit ces choses, afin que ma joie soit en vous, et que votre joie soit parfaite." },
        { book: "1 Pierre", chapter: 1, verse: 8, text: "vous l'aimez sans l'avoir vu, vous croyez en lui sans le voir encore, vous réjouissant d'une joie ineffable et glorieuse," }
      ],
      "espoir": [
        { book: "Romains", chapter: 15, verse: 13, text: "Que le Dieu de l'espérance vous remplisse de toute joie et de toute paix dans la foi, pour que vous abondiez en espérance, par la puissance du Saint-Esprit!" },
        { book: "Jérémie", chapter: 29, verse: 11, text: "Car je connais les projets que j'ai formés sur vous, dit l'Éternel, projets de paix et non de malheur, afin de vous donner un avenir et de l'espérance." },
        { book: "1 Pierre", chapter: 1, verse: 3, text: "Béni soit Dieu, le Père de notre Seigneur Jésus-Christ, qui, selon sa grande miséricorde, nous a régénérés, pour une espérance vivante, par la résurrection de Jésus-Christ d'entre les morts," },
        { book: "Hébreux", chapter: 6, verse: 19, text: "Cette espérance, nous la possédons comme une ancre de l'âme, sûre et solide;" }
      ],
      "sagesse": [
        { book: "Proverbes", chapter: 1, verse: 7, text: "La crainte de l'Éternel est le commencement de la science; Les insensés méprisent la sagesse et l'instruction." },
        { book: "Jacques", chapter: 1, verse: 5, text: "Si quelqu'un d'entre vous manque de sagesse, qu'il la demande à Dieu, qui donne à tous simplement et sans reproche, et elle lui sera donnée." },
        { book: "Proverbes", chapter: 3, verse: 13, text: "Heureux l'homme qui a trouvé la sagesse, Et l'homme qui possède l'intelligence!" },
        { book: "Ecclésiaste", chapter: 7, verse: 12, text: "Car à l'ombre de la sagesse on est abrité comme à l'ombre de l'argent; mais un avantage de la science, c'est que la sagesse fait vivre ceux qui la possèdent." }
      ],
      "pardon": [
        { book: "1 Jean", chapter: 1, verse: 9, text: "Si nous confessons nos péchés, il est fidèle et juste pour nous les pardonner, et pour nous purifier de toute iniquité." },
        { book: "Matthieu", chapter: 6, verse: 14, text: "Si vous pardonnez aux hommes leurs offenses, votre Père céleste vous pardonnera aussi;" },
        { book: "Colossiens", chapter: 3, verse: 13, text: "Supportez-vous les uns les autres, et, si l'un a sujet de se plaindre de l'autre, pardonnez-vous réciproquement. De même que Christ vous a pardonné, pardonnez-vous aussi." },
        { book: "Éphésiens", chapter: 4, verse: 32, text: "Soyez bons les uns envers les autres, compatissants, vous pardonnant réciproquement, comme Dieu vous a pardonné en Christ." }
      ],
      "prière": [
        { book: "1 Thessaloniciens", chapter: 5, verse: 17, text: "Priez sans cesse." },
        { book: "Philippiens", chapter: 4, verse: 6, text: "Ne vous inquiétez de rien; mais en toute chose faites connaître vos besoins à Dieu par des prières et des supplications, avec des actions de grâces." },
        { book: "Matthieu", chapter: 6, verse: 9, text: "Voici donc comment vous devez prier: Notre Père qui es aux cieux! Que ton nom soit sanctifié;" },
        { book: "Jacques", chapter: 5, verse: 16, text: "Confessez donc vos péchés les uns aux autres, et priez les uns pour les autres, afin que vous soyez guéris. La prière fervente du juste a une grande efficace." }
      ]
    };

    const termLower = term.toLowerCase();
    const matchingEntries = [];
    
    for (const [key, verses] of Object.entries(mockVerses)) {
      if (key.includes(termLower) || termLower.includes(key)) {
        matchingEntries.push(...verses);
      }
    }
    
    const uniqueResults = matchingEntries.filter((verse, index, arr) => 
      arr.findIndex(v => v.book === verse.book && v.chapter === verse.chapter && v.verse === verse.verse) === index
    );
    
    return uniqueResults.slice(0, 10);
  };

  const searchBibleConcordance = async (searchTerm) => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      const mockResults = generateConcordanceResults(searchTerm.trim());
      setResults(mockResults);
    } catch (error) {
      console.error("Erreur de recherche:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    searchBibleConcordance(searchTerm);
  };

  const handleSuggestionClick = (term) => {
    setSearchTerm(term);
    searchBibleConcordance(term);
  };

  const openYouVersionConcordance = () => {
    const searchUrl = searchTerm 
      ? `https://www.bible.com/search/bible?q=${encodeURIComponent(searchTerm)}`
      : 'https://www.bible.com/';
    window.open(searchUrl, '_blank');
  };

  const highlightSearchTerm = (text, term) => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark style="background: #fef3c7; color: #92400e; padding: 2px 4px; border-radius: 4px;">$1</mark>');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(124, 58, 237, 0.98) 100%)',
      fontFamily: 'Inter, sans-serif'
    }}>
      {/* En-tête */}
      <div style={{
        padding: '40px 20px',
        textAlign: 'center',
        color: 'white'
      }}>
        <button 
          onClick={onGoBack}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          ← Retour à l'Étude
        </button>
        
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '800',
          margin: '0 0 10px 0'
        }}>
          📖 Bible de Concordance
        </h1>
        
        <p style={{
          fontSize: '1.1rem',
          opacity: 0.9
        }}>
          Explorez les Écritures par mots-clés et personnages bibliques
        </p>

        {/* Onglets de navigation */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          marginTop: '24px'
        }}>
          <button
            onClick={() => setActiveTab('concordance')}
            style={{
              background: activeTab === 'concordance' ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            🔍 Concordance
          </button>
          <button
            onClick={() => setActiveTab('characters')}
            style={{
              background: activeTab === 'characters' ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            👥 Personnages Bibliques
          </button>
        </div>
      </div>

      {/* Contenu selon l'onglet actif */}
      {activeTab === 'concordance' ? (
        // SECTION CONCORDANCE EXISTANTE
        <>
          {/* Zone de recherche concordance */}
          <div style={{
            maxWidth: '800px',
            margin: '20px auto 0',
            padding: '0 20px'
          }}>
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '30px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{
                margin: '0 0 20px 0',
                color: '#333',
                fontSize: '18px',
                fontWeight: 'bold'
              }}>
                🔍 Recherche par Mots-Clés
              </h3>
              <form onSubmit={handleSearchSubmit}>
                <div style={{
                  display: 'flex',
                  gap: '10px',
                  marginBottom: '20px'
                }}>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Rechercher un mot dans la Bible..."
                    style={{
                      flex: 1,
                      padding: '15px',
                      border: '1px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px'
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                      background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                      color: 'white',
                      border: 'none',
                      padding: '15px 20px',
                      borderRadius: '8px',
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      opacity: isLoading ? 0.6 : 1,
                      minWidth: '100px'
                    }}
                  >
                    {isLoading ? 'Recherche...' : 'Rechercher'}
                  </button>
                  
                  {/* BOUTON GEMINI POUR CONCORDANCE */}
                  <button
                    type="button"
                    onClick={handleGeminiConcordance}
                    disabled={isLoading || !searchTerm.trim()}
                    style={{
                      background: 'linear-gradient(135deg, #00d2d3, #54a0ff)',
                      color: 'white',
                      border: 'none',
                      padding: '15px 20px',
                      borderRadius: '8px',
                      cursor: isLoading || !searchTerm.trim() ? 'not-allowed' : 'pointer',
                      opacity: isLoading || !searchTerm.trim() ? 0.6 : 1,
                      minWidth: '110px',
                      fontSize: '14px',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                    title="Enrichir la concordance avec Gemini AI"
                  >
                    🤖 Gemini
                  </button>
                </div>
              </form>

              {/* Section des 30 thèmes de la sainte doctrine */}
              <div style={{ marginBottom: '40px' }}>
                <h3 style={{
                  textAlign: 'center',
                  color: '#475569',
                  fontSize: '1.3rem',
                  fontWeight: '700',
                  marginBottom: '24px',
                  background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  ✨ Suggestions populaires : les 30 thèmes de la sainte doctrine
                </h3>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '12px',
                  maxWidth: '1200px',
                  margin: '0 auto'
                }}>
                  {[
                    'Salut', 'Grâce', 'Foi', 'Amour', 'Paix', 'Joie', 
                    'Espérance', 'Pardon', 'Rédemption', 'Justification',
                    'Sanctification', 'Résurrection', 'Vie éternelle', 'Royaume de Dieu',
                    'Repentance', 'Baptême', 'Saint-Esprit', 'Prière',
                    'Louange', 'Adoration', 'Obéissance', 'Humilité',
                    'Compassion', 'Miséricorde', 'Vérité', 'Sagesse',
                    'Justice', 'Sainteté', 'Providence', 'Gloire'
                  ].map((theme) => (
                    <button
                      key={theme}
                      onClick={() => {
                        setSearchTerm(theme);
                        searchBibleConcordance(theme);
                      }}
                      style={{
                        background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.9))',
                        border: '2px solid rgba(139, 92, 246, 0.2)',
                        color: '#7c3aed',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '600',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
                        e.target.style.color = 'white';
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 4px 16px rgba(139, 92, 246, 0.3)';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.background = 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.9))';
                        e.target.style.color = '#7c3aed';
                        e.target.style.transform = 'translateY(0)';
                        e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                      }}
                    >
                      {theme}
                    </button>
                  ))}
                </div>
              </div>

              {/* Suggestions rapides classiques */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '12px',
                justifyContent: 'center',
                marginBottom: '30px'
              }}>
                <p style={{
                  width: '100%',
                  textAlign: 'center',
                  color: '#64748b',
                  fontSize: '14px',
                  fontWeight: '500',
                  margin: '0 0 16px 0'
                }}>
                  Recherches rapides :
                </p>
                {['miracle', 'prophétie', 'temple', 'alliance', 'bénédiction', 'péché', 'création', 'jugement'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setSearchTerm(suggestion)}
                    style={{
                      background: 'rgba(255, 255, 255, 0.9)',
                      border: '2px solid rgba(139, 92, 246, 0.3)',
                      color: '#7c3aed',
                      padding: '8px 16px',
                      borderRadius: '20px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              {/* Bouton YouVersion */}
              <div style={{
                textAlign: 'center'
              }}>
                <button
                  onClick={openYouVersionConcordance}
                  style={{
                    background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  🔗 Ouvrir sur YouVersion
                </button>
              </div>
            </div>
          </div>
        </>
      ) : (
        // NOUVELLE SECTION PERSONNAGES BIBLIQUES  
        <>
          {/* Zone de recherche personnages */}
          <div style={{
            maxWidth: '800px',
            margin: '20px auto 0',
            padding: '0 20px'
          }}>
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '30px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{
                margin: '0 0 20px 0',
                color: '#333',
                fontSize: '18px',
                fontWeight: 'bold'
              }}>
                👥 Recherche de Personnages Bibliques
              </h3>
              
              {!selectedCharacter ? (
                <>
                  <div style={{
                    marginBottom: '20px'
                  }}>
                    <input
                      type="text"
                      value={characterSearchTerm}
                      onChange={(e) => setCharacterSearchTerm(e.target.value)}
                      placeholder="Tapez le nom d'un personnage biblique..."
                      style={{
                        width: '100%',
                        padding: '15px',
                        border: '1px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '16px',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>

                  {/* Liste filtrée des personnages */}
                  <div className="biblical-characters-grid" style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                    gap: '10px',
                    maxHeight: '350px',
                    overflowY: 'auto',
                    border: '1px solid #eee',
                    borderRadius: '8px',
                    padding: '16px',
                    width: '100%',
                    boxSizing: 'border-box'
                  }}>
                    {biblicalCharacters
                      .filter(character => 
                        characterSearchTerm === '' || 
                        character.toLowerCase().includes(characterSearchTerm.toLowerCase())
                      )
                      .map(character => (
                        <button
                          key={character}
                          onClick={() => generateCharacterHistory(character)}
                          className="biblical-character-btn"
                          style={{
                            background: 'rgba(139, 92, 246, 0.1)',
                            border: '1px solid rgba(139, 92, 246, 0.3)',
                            color: '#7c3aed',
                            padding: '12px 8px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '13px',
                            fontWeight: '500',
                            transition: 'all 0.3s ease',
                            textAlign: 'center',
                            width: '100%',
                            boxSizing: 'border-box',
                            minHeight: '48px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                          onMouseOver={(e) => {
                            e.target.style.background = 'rgba(139, 92, 246, 0.2)';
                            e.target.style.transform = 'translateY(-1px)';
                          }}
                          onMouseOut={(e) => {
                            e.target.style.background = 'rgba(139, 92, 246, 0.1)';
                            e.target.style.transform = 'translateY(0)';
                          }}
                        >
                          {character}
                        </button>
                      ))}}}
                  </div>

                  {characterSearchTerm && biblicalCharacters.filter(c => 
                    c.toLowerCase().includes(characterSearchTerm.toLowerCase())
                  ).length === 0 && (
                    <div style={{
                      textAlign: 'center',
                      padding: '20px',
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      Aucun personnage trouvé pour "{characterSearchTerm}"
                    </div>
                  )}
                </>
              ) : (
                // Affichage de l'histoire du personnage sélectionné
                <div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '20px'
                  }}>
                    <h2 style={{
                      margin: 0,
                      color: '#333',
                      fontSize: '20px',
                      fontWeight: 'bold'
                    }}>
                      📜 Histoire de {selectedCharacter}
                    </h2>
                    <div style={{
                      display: 'flex',
                      gap: '12px',
                      alignItems: 'center'
                    }}>
                      {/* BOUTON GEMINI POUR PERSONNAGE SÉLECTIONNÉ */}
                      <button
                        onClick={handleGeminiCharacter}
                        disabled={isCharacterLoading}
                        style={{
                          background: 'linear-gradient(135deg, #00d2d3, #54a0ff)',
                          color: 'white',
                          border: 'none',
                          padding: '10px 16px',
                          borderRadius: '6px',
                          cursor: isCharacterLoading ? 'not-allowed' : 'pointer',
                          opacity: isCharacterLoading ? 0.6 : 1,
                          fontSize: '12px',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                        title="Enrichir avec Gemini AI"
                      >
                        🤖 Gemini
                      </button>
                      
                      <button
                        onClick={() => {
                          setSelectedCharacter(null);
                          setCharacterHistory('');
                          setCharacterSearchTerm('');
                        }}
                        style={{
                          background: 'rgba(107, 114, 128, 0.1)',
                          border: '1px solid rgba(107, 114, 128, 0.3)',
                          color: '#6b7280',
                          padding: '8px 16px',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        ← Retour à la liste
                      </button>
                    </div>
                  </div>

                  {isCharacterLoading ? (
                    <div style={{
                      textAlign: 'center',
                      padding: '60px 20px'
                    }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        border: '4px solid #e2e8f0',
                        borderTop: '4px solid #8b5cf6',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto 20px'
                      }} />
                      <p style={{
                        color: '#666',
                        fontSize: '16px',
                        margin: 0
                      }}>
                        Génération de l'histoire complète de {selectedCharacter}...
                      </p>
                      <p style={{
                        color: '#999',
                        fontSize: '12px',
                        margin: '8px 0 0'
                      }}>
                        Croisement des versets bibliques en cours
                      </p>
                    </div>
                  ) : (
                    <div style={{
                      background: 'linear-gradient(135deg, #f8fafc, #f1f5f9)',
                      border: '1px solid rgba(139, 92, 246, 0.2)',
                      borderRadius: '12px',
                      padding: '30px',
                      maxHeight: '700px',
                      overflowY: 'auto',
                      fontSize: '15px',
                      lineHeight: '1.7',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
                    }}>
                      <div dangerouslySetInnerHTML={{
                        __html: characterHistory
                          .replace(/\n/g, '<br>')
                          // Titre principal sur une ligne
                          .replace(/##\s(.+)/g, '<h2 style="color: #1e293b; margin: 24px 0 20px 0; font-size: 20px; font-weight: 700; border-bottom: 2px solid rgba(139, 92, 246, 0.3); padding-bottom: 8px; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">$1</h2>')
                          // Supprimer les ### et numérotation pour un style narratif
                          .replace(/###\s?\d*\.?\s*(.+)/g, '<p style="color: #1e293b; margin: 16px 0 12px 0; font-size: 16px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">$1</p>')
                          // Gras pour les passages importants
                          .replace(/\*\*(.+?)\*\*/g, '<strong style="color: #7c3aed; font-weight: 700;">$1</strong>')
                          // Italique pour les mots étrangers et citations
                          .replace(/\*(.+?)\*/g, '<em style="color: #64748b; font-style: italic;">$1</em>')
                          // Versets cliquables
                          .replace(/(Exode|Lévitique|Nombres|Genèse|Deutéronome|Psaumes|Hébreux|Matthieu|Marc|Luc|Jean|Actes|Romains|1 Corinthiens|2 Corinthiens|Galates|Éphésiens|Philippiens|Colossiens)\s+(\d+):(\d+(?:-\d+)?)/g, 
                            '<span onclick="window.open(\'https://www.bible.com/search/bible?q=$1+$2%3A$3\', \'_blank\')" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 4px 8px; border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: 600; display: inline-block; margin: 2px; transition: all 0.3s ease;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'" title="Cliquer pour lire ce verset">📖 $1 $2:$3</span>')
                          // Créer des paragraphes narratifs
                          .replace(/([.!?])\s*<br>/g, '$1</p><p style="color: #374151; font-size: 15px; line-height: 1.7; margin: 12px 0; text-align: justify; text-indent: 20px;">')
                          .replace(/^/, '<p style="color: #374151; font-size: 15px; line-height: 1.7; margin: 12px 0; text-align: justify; text-indent: 20px;">')
                          .replace(/$/, '</p>')
                      }} />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Résultats de recherche concordance */}
      {activeTab === 'concordance' && (
        <div style={{
          maxWidth: '1000px',
          margin: '20px auto 0',
          padding: '0 20px'
        }}>
          {/* Résultats */}
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                border: '4px solid #e5e7eb',
                borderTop: '4px solid #8b5cf6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto'
              }}></div>
              <p style={{ color: 'white', marginTop: '15px' }}>
                Recherche en cours...
              </p>
            </div>
          ) : results.length > 0 ? (
            <div>
              <h2 style={{
                textAlign: 'center',
                color: 'white',
                fontSize: '1.5rem',
                marginBottom: '20px'
              }}>
                📋 {results.length} résultat(s) pour "{searchTerm}"
              </h2>
              <div style={{
                display: 'grid',
                gap: '20px'
              }}>
                {results.map((verse, index) => (
                  <div 
                    key={index}
                    style={{
                      background: 'white',
                      borderRadius: '12px',
                      padding: '20px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                      borderLeft: '4px solid #8b5cf6'
                    }}
                  >
                    <div style={{
                      color: '#7c3aed',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      marginBottom: '10px'
                    }}>
                      {verse.book} {verse.chapter}:{verse.verse}
                    </div>
                    <div 
                      style={{
                        color: '#374151',
                        lineHeight: '1.6'
                      }}
                      dangerouslySetInnerHTML={{ 
                        __html: highlightSearchTerm(verse.text, searchTerm) 
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          ) : searchTerm.length > 0 ? (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <h3 style={{ color: '#6b7280' }}>
                🔍 Aucun résultat pour "{searchTerm}"
              </h3>
              <p style={{ color: '#999', fontSize: '14px', marginTop: '10px' }}>
                Essayez avec d'autres termes ou consultez les suggestions.
              </p>
            </div>
          ) : (
            /* Message de bienvenue supprimé pour plus de clarté */
            null
          )}
        </div>
      )}

      {/* Styles CSS pour les animations */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default BibleConcordancePage;