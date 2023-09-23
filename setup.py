from setuptools import setup

setup(
    name='Dark Matter Mage',
    options={
        'build_apps': {
            'gui_apps': {
                'Dark Matter Mage': 'main.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/Asteroids/output.log',
            'log_append': False,

            # Specify which files are included with the distribution
            'include_patterns': [
                'assets/**/*'
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        }
    }
)