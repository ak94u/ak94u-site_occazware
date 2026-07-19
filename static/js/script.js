            // Permet à Tailwind de supporter le mode sombre par classe
            tailwind.config = {
                darkMode: 'class'
            }
            
            // Applique le thème sauvegardé dès le chargement pour éviter le flash blanc
            const savedTheme = localStorage.getItem('theme') || 'dark';
            if (savedTheme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }

        document.addEventListener("DOMContentLoaded", function() {
            // --- 1. Gestion des messages Flash ---
            const flashMessage = document.getElementById('flash-message');
            if (flashMessage) {
                setTimeout(function() {
                    flashMessage.classList.add('opacity-0');
                    setTimeout(function() {
                        flashMessage.remove();
                    }, 500);
                }, 3000);
            }

        // --- 2. Vérification et affichage initial des Cookies ---
        const cookieBanner = document.getElementById('cookie-banner');
        // Si le cookie existe déjà, on fait disparaître la bannière immédiatement sans attendre le clic
        if (cookieBanner && document.cookie.split('; ').find(row => row.startsWith('consent='))) {
            cookieBanner.style.display = 'none';
        }
    });

   // --- 3. Action de consentement des cookies ---
        function acceptCookies() {
            fetch('/consent')
                .then(response => {
                    if (response.ok) {

                        const cookieBanner = document.getElementById('cookie-banner');
                        const pageWrapper = document.getElementById('page-wrapper');

                        // Animation fluide : bannière + fond flou disparaissent ensemble
                        if (cookieBanner) {
                            cookieBanner.classList.add(
                                'opacity-0',
                                'translate-y-4',
                                'pointer-events-none'
                            );
                        }

                        if (pageWrapper) {
                            pageWrapper.classList.add(
                                'opacity-100',      // assure la transition
                                'transition-all',
                                'duration-300'
                            );

                            // Retirer le flou immédiatement pour synchroniser
                            pageWrapper.classList.remove(
                                'blur-md',
                                'pointer-events-none',
                                'select-none'
                            );
                        }

                        // Suppression du DOM après animation (300ms)
                        setTimeout(() => {
                            if (cookieBanner) cookieBanner.remove();
                        }, 300);
                    }
                })
                .catch(error => console.error("Erreur lors du consentement:", error));
        }

        function modifierTheme(nouveauTheme) {
            // 1. On l'applique au HTML et au localStorage (votre logique actuelle)
            if (nouveauTheme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            localStorage.setItem('theme', nouveauTheme);

            // 2. LA NOUVEAUTÉ : On crée le cookie pour que Flask puisse le voir
            // (Ici réglé pour expirer dans 30 jours, comme dans votre code Flask)
            const maxAge = 60 * 60 * 24 * 30; 
            document.cookie = `theme=${nouveauTheme}; max-age=${maxAge}; path=/; SameSite=Lax`;
        }

        function switchMode(mode) {
        const formLogin = document.getElementById('form-login');
        const formRegister = document.getElementById('form-register');
        const tabLogin = document.getElementById('tab-login');
        const tabRegister = document.getElementById('tab-register');

        if (mode === 'register') {
            formLogin.classList.add('hidden');
            formRegister.classList.remove('hidden');
            
            tabRegister.className = "w-1/2 text-center pb-2 font-bold text-lg text-white border-b-2 border-white transition";
            tabLogin.className = "w-1/2 text-center pb-2 font-bold text-lg text-gray-500 border-b-2 border-transparent hover:text-gray-300 transition";
        } else {
            formRegister.classList.add('hidden');
            formLogin.classList.remove('hidden');
            
            tabLogin.className = "w-1/2 text-center pb-2 font-bold text-lg text-white border-b-2 border-white transition";
            tabRegister.className = "w-1/2 text-center pb-2 font-bold text-lg text-gray-500 border-b-2 border-transparent hover:text-gray-300 transition";
        }
    }

    // Permet de rester sur l'onglet inscription si le serveur renvoie une erreur d'inscription
    document.addEventListener("DOMContentLoaded", function() {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('mode') === 'inscription') {
            switchMode('register');
        }
    });

    // Le script reste identique pour déclencher la recherche
    document.addEventListener("DOMContentLoaded", function() {
        const form = document.getElementById('filter-form');
        document.querySelectorAll('.filter-checkbox').forEach(cb => {
            cb.addEventListener('change', () => form.submit());
        });
        document.querySelector('input[name="prix_max"]').addEventListener('change', () => form.submit());
    });

    // 1. On récupère le thème sauvegardé dans le navigateur, ou "dark" par défaut
    let activeTheme = localStorage.getItem('theme') || 'dark';

    function updateUI(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        const ball = document.getElementById('theme-toggle-ball');
        const icon = document.getElementById('theme-icon');

        if (!toggleBtn || !ball || !icon) return;

        if (theme === 'light') {
            toggleBtn.className = "relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-blue-600";
            ball.className = "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out translate-x-5 flex items-center justify-center text-xs";
            icon.innerText = '☀️';
            document.documentElement.classList.remove('dark');
        } else {
            toggleBtn.className = "relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-gray-300";
            ball.className = "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out translate-x-0 flex items-center justify-center text-xs";
            icon.innerText = '🌙';
            document.documentElement.classList.add('dark');
        }
    }

    // 2. On applique le thème immédiatement au chargement de la page
    updateUI(activeTheme);

    function toggleTheme() {
        // Inverse le thème
        activeTheme = activeTheme === "dark" ? "light" : "dark";

        // 3. Met à jour visuellement le bouton et le site instantanément
        updateUI(activeTheme);

        // 4. Sauvegarde dans le navigateur pour les autres pages
        localStorage.setItem('theme', activeTheme);

        // 5. On informe quand même Flask en arrière-plan (sans recharger la page)
        fetch(`/set-theme/${activeTheme}`, { method: "POST" })
            .catch(err => console.log("Sauvegarde cookie en arrière-plan échouée, mais le localStorage prend le relais."));
    }

    // 2. On surcharge la fonction de réinitialisation pour intercepter le clic
    function reinitialiserConsentement() {
        // Supprime le cookie
        document.cookie = "consent=; max-age=0; path=/; SameSite=Lax";
        
        // Sauvegarde la date
        const now = new Date();
        const formattedDate = now.toLocaleString('fr-FR', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        localStorage.setItem('lastCookieUpdate', formattedDate);
        
        // Recharge la page
        window.location.reload();
    }
