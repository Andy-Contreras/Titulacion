const colors = require('tailwindcss/colors');

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
        '../../**/*.js',
        '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                yellow: colors.amber,
                'custom-gray': '#343c44',
                'custom-boton': '#14a4bc',
                'custom-green': '#2ca444',
                'custom-red': '#dc3444',
                'custom-blue': '#087cfc',
                'custom-purple': '#6b5b95',  // Ejemplo de color personalizado adicional
            },
            screens: {
                'xs': '480px',
                '3xl': '1600px',
            },
            // Otras extensiones que puedes considerar
            spacing: {
                '128': '32rem',  // Ejemplo de tamaño personalizado
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
        require('@tailwindcss/aspect-ratio'),
    ],
};
