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

    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = localStorage.getItem('theme') || 'dark';
        
        if (currentTheme === 'dark') {
            // Passer au mode clair
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            updateUI('light');
        } else {
            // Passer au mode sombre (de base)
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            updateUI('dark');
        }
    }

    function updateUI(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        const ball = document.getElementById('theme-toggle-ball');
        const icon = document.getElementById('theme-icon');

        if (theme === 'light') {
            // Style quand le bouton est activé (Thème Blanc)
            toggleBtn.classList.remove('bg-gray-300', 'dark:bg-zinc-700');
            toggleBtn.classList.add('bg-blue-600');
            ball.classList.add('translate-x-5');
            ball.classList.remove('translate-x-0');
            icon.innerText = '☀️';
        } else {
            // Style quand le bouton est désactivé (Thème de base / Sombre)
            toggleBtn.classList.add('bg-gray-300', 'dark:bg-zinc-700');
            toggleBtn.classList.remove('bg-blue-600');
            ball.classList.add('translate-x-0');
            ball.classList.remove('translate-x-5');
            icon.innerText = '🌙';
        }
    }

    // Initialisation au chargement de la page
    const activeTheme = localStorage.getItem('theme') || 'dark';
    updateUI(activeTheme);