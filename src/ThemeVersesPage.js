import React, { useState, useEffect } from 'react';

const ThemeVersesPage = ({ theme, onGoBack }) => {
  const [verses, setVerses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Base de données étendue avec 20+ versets par thème
  const themesDatabase = {
    "salut": [
      { book: "Éphésiens", chapter: 2, verse: 8, text: "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu." },
      { book: "Jean", chapter: 3, verse: 16, text: "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle." },
      { book: "Romains", chapter: 10, verse: 9, text: "Si tu confesses de ta bouche le Seigneur Jésus, et si tu crois dans ton cœur que Dieu l'a ressuscité des morts, tu seras sauvé." },
      { book: "Actes", chapter: 4, verse: 12, text: "Il n'y a de salut en aucun autre; car il n'y a sous le ciel aucun autre nom qui ait été donné parmi les hommes, par lequel nous devions être sauvés." },
      { book: "1 Pierre", chapter: 1, verse: 18, text: "sachant que ce n'est pas par des choses périssables, par de l'argent ou de l'or, que vous avez été rachetés de la vaine manière de vivre que vous aviez héritée de vos pères," },
      { book: "Tite", chapter: 3, verse: 5, text: "il nous a sauvés, non à cause des œuvres de justice que nous aurions faites, mais selon sa miséricorde, par le baptême de la régénération et le renouvellement du Saint-Esprit," },
      { book: "2 Timothée", chapter: 1, verse: 9, text: "qui nous a sauvés, et nous a adressé une sainte vocation, non à cause de nos œuvres, mais selon son propre dessein, et selon la grâce qui nous a été donnée en Jésus-Christ avant les temps éternels," },
      { book: "Hébreux", chapter: 2, verse: 3, text: "comment échapperons-nous en négligeant un si grand salut, qui, annoncé d'abord par le Seigneur, nous a été confirmé par ceux qui l'ont entendu," },
      { book: "1 Jean", chapter: 5, verse: 11, text: "Et voici ce témoignage, c'est que Dieu nous a donné la vie éternelle, et que cette vie est dans son Fils." },
      { book: "Romains", chapter: 1, verse: 16, text: "Car je n'ai point honte de l'Évangile: c'est une puissance de Dieu pour le salut de quiconque croit, du Juif premièrement, puis du Grec." },
      { book: "Luc", chapter: 19, verse: 10, text: "Car le Fils de l'homme est venu chercher et sauver ce qui était perdu." },
      { book: "1 Timothée", chapter: 2, verse: 4, text: "qui veut que tous les hommes soient sauvés et parviennent à la connaissance de la vérité." },
      { book: "Ésaïe", chapter: 53, verse: 5, text: "Mais il était blessé pour nos péchés, Brisé pour nos iniquités; Le châtiment qui nous donne la paix est tombé sur lui, Et c'est par ses meurtrissures que nous sommes guéris." },
      { book: "Psaume", chapter: 3, verse: 8, text: "Le salut est à l'Éternel! Que ta bénédiction soit sur ton peuple! -Pause." },
      { book: "Joël", chapter: 2, verse: 32, text: "Alors quiconque invoquera le nom de l'Éternel sera sauvé; Le salut sera sur la montagne de Sion et à Jérusalem, Comme a dit l'Éternel, Et parmi les réchappés que l'Éternel appellera." },
      { book: "Apocalypse", chapter: 7, verse: 10, text: "Et ils criaient d'une voix forte, en disant: Le salut est à notre Dieu qui est assis sur le trône, et à l'agneau." },
      { book: "Philippe", chapter: 2, verse: 12, text: "Ainsi, mes bien-aimés, comme vous avez toujours obéi, travaillez à votre salut avec crainte et tremblement, non seulement comme en ma présence, mais bien plus encore maintenant que je suis absent;" },
      { book: "Ésaïe", chapter: 12, verse: 3, text: "Vous puiserez de l'eau avec joie Aux sources du salut," },
      { book: "Psaume", chapter: 27, verse: 1, text: "L'Éternel est ma lumière et mon salut: De qui aurais-je crainte? L'Éternel est le soutien de ma vie: De qui aurais-je peur?" },
      { book: "Habacuc", chapter: 3, verse: 18, text: "Toutefois, je veux me réjouir en l'Éternel, Je veux me réjouir dans le Dieu de mon salut." },
      { book: "2 Corinthiens", chapter: 6, verse: 2, text: "Il dit: Au temps favorable je t'ai exaucé, Au jour du salut je t'ai secouru. Voici maintenant le temps favorable, voici maintenant le jour du salut." },
      { book: "1 Pierre", chapter: 2, verse: 2, text: "désirez, comme des enfants nouveau-nés, le lait spirituel et pur, afin que par lui vous croissiez pour le salut," }
    ],
    "grâce": [
      { book: "Éphésiens", chapter: 2, verse: 8, text: "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu." },
      { book: "Romains", chapter: 3, verse: 24, text: "et ils sont gratuitement justifiés par sa grâce, par le moyen de la rédemption qui est en Jésus-Christ." },
      { book: "2 Corinthiens", chapter: 12, verse: 9, text: "et il m'a dit: Ma grâce te suffit, car ma puissance s'accomplit dans la faiblesse. Je me glorifierai donc bien plus volontiers de mes faiblesses, afin que la puissance de Christ repose sur moi." },
      { book: "Tite", chapter: 2, verse: 11, text: "Car la grâce de Dieu, source de salut pour tous les hommes, a été manifestée." },
      { book: "Hébreux", chapter: 4, verse: 16, text: "Approchons-nous donc avec assurance du trône de la grâce, afin d'obtenir miséricorde et de trouver grâce, pour être secourus dans nos besoins." },
      { book: "Jean", chapter: 1, verse: 16, text: "Et nous avons tous reçu de sa plénitude, et grâce pour grâce." },
      { book: "Romains", chapter: 5, verse: 20, text: "Or, la loi est intervenue pour que l'offense abondât, mais là où le péché a abondé, la grâce a surabondé," },
      { book: "1 Pierre", chapter: 5, verse: 10, text: "Le Dieu de toute grâce, qui vous a appelés en Jésus-Christ à sa gloire éternelle, après que vous aurez souffert un peu de temps, vous perfectionnera lui-même, vous affermira, vous fortifiera, vous rendra inébranlables." },
      { book: "Actes", chapter: 15, verse: 11, text: "Mais c'est par la grâce du Seigneur Jésus que nous croyons être sauvés, de la même manière qu'eux." },
      { book: "Galates", chapter: 2, verse: 21, text: "Je ne rejette pas la grâce de Dieu; car si la justice vient de la loi, Christ est donc mort en vain." },
      { book: "Romains", chapter: 11, verse: 6, text: "Or, si c'est par grâce, ce n'est plus par les œuvres; autrement la grâce n'est plus une grâce. Et si c'est par les œuvres, ce n'est plus une grâce; autrement l'œuvre n'est plus une œuvre." },
      { book: "Éphésiens", chapter: 1, verse: 7, text: "En lui nous avons la rédemption par son sang, la rémission des péchés, selon la richesse de sa grâce," },
      { book: "2 Timothée", chapter: 2, verse: 1, text: "Toi donc, mon enfant, fortifie-toi dans la grâce qui est en Jésus-Christ." },
      { book: "Jacques", chapter: 4, verse: 6, text: "Il accorde, au contraire, une grâce plus excellente; c'est pourquoi l'Écriture dit: Dieu résiste aux orgueilleux, Mais il fait grâce aux humbles." },
      { book: "1 Corinthiens", chapter: 15, verse: 10, text: "Par la grâce de Dieu je suis ce que je suis, et sa grâce envers moi n'a pas été vaine; loin de là, j'ai travaillé plus qu'eux tous, non pas moi toutefois, mais la grâce de Dieu qui est avec moi." },
      { book: "Psaume", chapter: 84, verse: 11, text: "Car l'Éternel Dieu est un soleil et un bouclier, L'Éternel donne la grâce et la gloire, Il ne refuse aucun bien à ceux qui marchent dans l'intégrité." },
      { book: "Zacharie", chapter: 4, verse: 7, text: "Qui es-tu, grande montagne, devant Zorobabel? Tu seras aplanie. Il posera la pierre principale au milieu des acclamations: Grâce, grâce pour elle!" },
      { book: "Nombres", chapter: 6, verse: 25, text: "Que l'Éternel fasse luire sa face sur toi, et qu'il t'accorde sa grâce!" },
      { book: "Proverbes", chapter: 3, verse: 34, text: "Il se moque des moqueurs, Mais il fait grâce aux humbles;" },
      { book: "Luc", chapter: 2, verse: 40, text: "Or, l'enfant croissait et se fortifiait. Il était rempli de sagesse, et la grâce de Dieu était sur lui." },
      { book: "Colossiens", chapter: 4, verse: 6, text: "Que votre parole soit toujours accompagnée de grâce, assaisonnée de sel, afin que vous sachiez comment il faut répondre à chacun." },
      { book: "Hébreux", chapter: 13, verse: 9, text: "Ne vous laissez pas entraîner par des doctrines diverses et étrangères; car il est bon que le cœur soit affermi par la grâce, et non par des aliments qui n'ont servi de rien à ceux qui s'y sont attachés." }
    ],
    "foi": [
      { book: "Hébreux", chapter: 11, verse: 1, text: "Or la foi est une ferme assurance des choses qu'on espère, une démonstration de celles qu'on ne voit point." },
      { book: "Romains", chapter: 10, verse: 17, text: "Ainsi la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ." },
      { book: "Éphésiens", chapter: 2, verse: 8, text: "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu." },
      { book: "Marc", chapter: 11, verse: 22, text: "Jésus prit la parole, et leur dit: Ayez foi en Dieu." },
      { book: "Habacuc", chapter: 2, verse: 4, text: "Voici, son âme s'est enflée, elle n'est pas droite en lui; Mais le juste vivra par sa foi." },
      { book: "Jacques", chapter: 2, verse: 17, text: "Il en est ainsi de la foi: si elle n'a pas les œuvres, elle est morte en elle-même." },
      { book: "1 Corinthiens", chapter: 13, verse: 13, text: "Maintenant donc ces trois choses demeurent: la foi, l'espérance, la charité; mais la plus grande de ces choses, c'est la charité." },
      { book: "Matthieu", chapter: 17, verse: 20, text: "C'est à cause de votre incrédulité, leur dit Jésus. Je vous le dis en vérité, si vous aviez de la foi comme un grain de sénevé, vous diriez à cette montagne: Transporte-toi d'ici là, et elle se transporterait; rien ne vous serait impossible." },
      { book: "Hébreux", chapter: 11, verse: 6, text: "Or sans la foi il est impossible de lui être agréable; car il faut que celui qui s'approche de Dieu croie que Dieu existe, et qu'il est le rémunérateur de ceux qui le cherchent." },
      { book: "Galates", chapter: 3, verse: 26, text: "Car vous êtes tous fils de Dieu par la foi en Jésus-Christ;" },
      { book: "Romains", chapter: 1, verse: 17, text: "parce qu'en lui est révélée la justice de Dieu par la foi et pour la foi, selon qu'il est écrit: Le juste vivra par la foi." },
      { book: "2 Corinthiens", chapter: 5, verse: 7, text: "(car nous marchons par la foi et non par la vue)," },
      { book: "1 Pierre", chapter: 1, verse: 7, text: "afin que l'épreuve de votre foi, plus précieuse que l'or périssable (qui cependant est éprouvé par le feu), ait pour résultat la louange, la gloire et l'honneur, lorsque Jésus-Christ apparaîtra:" },
      { book: "Jacques", chapter: 1, verse: 3, text: "sachant que l'épreuve de votre foi produit la patience." },
      { book: "Marc", chapter: 9, verse: 23, text: "Jésus lui dit: Si tu peux!... Tout est possible à celui qui croit." },
      { book: "Luc", chapter: 17, verse: 5, text: "Les apôtres dirent au Seigneur: Augmente-nous la foi." },
      { book: "1 Timothée", chapter: 6, verse: 12, text: "Combats le bon combat de la foi, saisis la vie éternelle, à laquelle tu as été appelé, et pour laquelle tu as fait une belle confession en présence d'un grand nombre de témoins." },
      { book: "Actes", chapter: 16, verse: 31, text: "Paul et Silas répondirent: Crois au Seigneur Jésus, et tu seras sauvé, toi et ta famille." },
      { book: "Romains", chapter: 14, verse: 23, text: "Mais celui qui a des doutes au sujet de ce qu'il mange est condamné, parce qu'il n'agit pas par conviction. Tout ce qui n'est pas le produit d'une conviction est péché." },
      { book: "Galates", chapter: 2, verse: 20, text: "J'ai été crucifié avec Christ; et si je vis, ce n'est plus moi qui vis, c'est Christ qui vit en moi; si je vis maintenant dans la chair, je vis dans la foi au Fils de Dieu, qui m'a aimé et qui s'est livré lui-même pour moi." },
      { book: "Hébreux", chapter: 12, verse: 2, text: "ayant les regards sur Jésus, le chef et le consommateur de la foi, qui, en vue de la joie qui lui était réservée, a souffert la croix, méprisé l'ignominie, et s'est assis à la droite du trône de Dieu." },
      { book: "1 Jean", chapter: 5, verse: 4, text: "parce que tout ce qui est né de Dieu triomphe du monde; et la victoire qui triomphe du monde, c'est notre foi." }
    ]
    // Nous pouvons ajouter d'autres thèmes ici...
  };

  useEffect(() => {
    loadThemeVerses();
  }, [theme]);

  const loadThemeVerses = () => {
    setIsLoading(true);
    
    // Simuler un chargement
    setTimeout(() => {
      const themeKey = theme.toLowerCase();
      const themeVerses = themesDatabase[themeKey] || [];
      setVerses(themeVerses);
      setIsLoading(false);
    }, 800);
  };

  if (isLoading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center', color: '#667eea' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '20px',
            animation: 'spin 2s linear infinite'
          }}>📖</div>
          <h2>Recherche des versets sur "{theme}"...</h2>
          <p>Compilation de plus de 20 versets bibliques</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
      padding: '20px'
    }}>
      {/* Header avec retour */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        marginBottom: '30px',
        maxWidth: '1200px',
        margin: '0 auto 30px auto'
      }}>
        <button 
          onClick={onGoBack}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '700',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ← Retour
        </button>
        
        <div>
          <h1 style={{ 
            fontSize: '32px', 
            fontWeight: '700',
            margin: '0',
            color: '#2c3e50',
            fontFamily: "'Montserrat', sans-serif"
          }}>
            📖 Versets sur "{theme}"
          </h1>
          <p style={{ 
            margin: '5px 0 0 0',
            color: '#667eea',
            fontSize: '16px'
          }}>
            {verses.length} versets trouvés
          </p>
        </div>
      </div>

      {/* Liste des versets */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {verses.length > 0 ? (
          <div style={{
            display: 'grid',
            gap: '20px'
          }}>
            {verses.map((verse, index) => (
              <div
                key={index}
                style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid rgba(102, 126, 234, 0.1)',
                  boxShadow: '0 8px 32px rgba(102, 126, 234, 0.1)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 12px 48px rgba(102, 126, 234, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 8px 32px rgba(102, 126, 234, 0.1)';
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: '20px'
                }}>
                  <div style={{ flex: 1 }}>
                    <p style={{
                      fontSize: '18px',
                      lineHeight: '1.6',
                      color: '#2c3e50',
                      margin: '0 0 12px 0',
                      fontFamily: "'Georgia', serif"
                    }}>
                      "{verse.text}"
                    </p>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '700',
                      color: '#667eea',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                      fontFamily: "'Montserrat', sans-serif"
                    }}>
                      {verse.book} {verse.chapter}:{verse.verse}
                    </div>
                  </div>
                  <div style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    borderRadius: '20px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    minWidth: '40px',
                    textAlign: 'center'
                  }}>
                    {index + 1}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#667eea'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📚</div>
            <h3>Aucun verset trouvé pour "{theme}"</h3>
            <p>Ce thème n'est pas encore disponible dans notre base de données.</p>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ThemeVersesPage;