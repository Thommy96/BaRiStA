|release| |nbsp| |license|

.. |release| image:: https://img.shields.io/github/v/release/digitalphonetics/adviser?sort=semver
   :target: https://github.com/DigitalPhonetics/adviser/releases
.. |license| image:: https://img.shields.io/github/license/digitalphonetics/adviser
   :target: #license
.. |nbsp| unicode:: 0xA0
   :trim:
   
BaRiStA
========
BaRiStA is a task-oriented dialogue system that provides information and assistance on finding restaurants and bars in Stuttgart. It is based on the ADVISER toolkit. You can see instructions how to install and setup the toolkit below. In order to use the text-based version of BaRiStA execute the script ``run_chat.py`` by running:

.. code-block:: bash
   
   python run_chat.py restaurants_stuttgart
   
For more options such as ASR, TTS or interface refer to the ADVISER documentation below.

ADVISER Documentation
=============

    Please see the `documentation <https://digitalphonetics.github.io/adviser/>`_ for more details.

Installation
============

Note: Adviser 2.0 is currently only tested on Linux and Mac (Windows is possible using WSL2 (Ubuntu), for M1 chips see the extra section near the bottom of this file).

Downloading the code
--------------------

If ``Git`` is not installated on your machine, just download the Adviser 2.0 file available in ``relases`` section. Then unzip and navigate to the main folder.
Note that this method has some disadvantages (you'll only be able to run basic text-to-text terminal conversations).

Cloning the repository (recommended)
------------------------------------

If ``Git`` is installed on your machine, you may instead clone the repository by entering in a terminal window:

.. code-block:: bash

    git clone https://github.com/DigitalPhonetics/adviser.git

System Library Requirements
---------------------------

* If you want to use speech in-/output, please make sure you have the `hdf5`, `portaudio` and `sndfile` libraries installed.
* If you want to make use of the function ``services.service.Service.draw_system_graph``,
you will need to install the ``graphviz`` library via your system's package manager.
If you can't install it (no sufficient user rights), don't use this function in your scripts.

On Ubuntu e.g.:

``sudo apt-get install graphviz``

On Mac, you will need to install homebrew by executing:

``/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"``

and then calling ``brew install graphviz``.

For other OS please see https://graphviz.gitlab.io/download/.


Install python requirements with pip
------------------------------------

ADvISER needs to be executed in a Python3 environment.

Once you obtained the code, navigate to its top level directory where you will find the file
``requirements_base.txt``, which lists all modules you need to run a basic text-to-text version of ADvISER. We suggest to create a
virtual environment from the top level directory, as shown below, followed by installing the necessary packages.


1. (Requires pip or pip3) Make sure you have virtualenv installed by executing

.. code-block:: bash

    python3 -m pip install --user virtualenv

2. Create the virtual environment (replace envname with a name of your choice)

.. code-block:: bash

    python3 -m venv <path-to-env>

3. Source the environment (this has to be repeated every time you want to use ADVISER inside a
new terminal session)

.. code-block:: bash

    source <path-to-env>/bin/activate

4. Install the required packages

.. code-block:: bash

    pip install -r requirements_base.txt 
 
(NOTE: or requirements_multimodal.txt if you want to use ASR / TTS)


5. Navigate to the adviser folder

.. code-block:: bash

    cd adviser

and, to make sure your installation is working, execute


.. code-block:: bash

    python run_chat.py lecturers
    
You can type text to chat with the system (confirm your utterance by pressing the ``Enter``-Key once) or type ``bye`` (followed by pressing the ``Enter``-Key once) to end the conversation.

To see more of the available options, run

.. code-block:: bash

    python run_chat.py --help


6. OPTIONAL: If you want to use multimodal functionallity, e.g. ASR / TTS/ ..., download the models via the script ``download_models.sh`` found in the top level folder

.. code-block:: bash

    sh download_models.sh
   
NOTE: this also requires you to install ``requirements_multimodal.txt`` in ``step 4``.

You can enable ASR / TTS by adding ``--asr`` and ``--tts`` to the command line options of ``run_chat.py`` (NOTE: for TTS, we recommend you run the code on a CUDA-enabled device and append ``--cuda`` to the command line options for drastic performance increase).

7. OPTIONAL: If you want to run the demo with all services enabled, please make sure you executed step 6 and installed the  ``requirements_multimodal.txt``. Then, additional requirements must be compiled by yourself - follow the guide in ``tools/OpenFace/how_to_install.md`` for this.

Then, try running 

``python run_demo_multidomain.py``



Instructions for Macs with M1 Chips 
===================================

In general, everything should work if you're using ``conda`` instead of ``pip``.
For pip users, the following installation instructions worked:

1. Install the system library requirements as stated above (using ``homebrew``).

2.  pip install -i https://pypi.anaconda.org/numba/label/wheels_experimental_m1/simple numba

3. Remove pyaudio from the requirements file and instead execute this command to install pyaudio:

.. code-block:: bash
    
    python -m pip install --global-option='build_ext' --global-option='-I/opt/homebrew/Cellar/portaudio/19.7.0/include' --global-option='-L/opt/homebrew/Cellar/portaudio/19.7.0/lib' pyaudio

4. Proceed with installing requirements as described above

5. Switch to the adviser folder ``cd adviser`` (containing the ``run_chat.py`` file)

6. Copy the snd library into the current folder:

.. code-block:: bash
    
    cp /opt/homebrew/lib/libsndfile.dylib

Building the documentation
==========================

1. Install the Python packages from ``requirements_doc.txt``.

2. Run ``PYTHONPATH=./adviser mkdocs build`` or ``PYTHONPATH=./adviser mkdocs gh-deploy`` for pushing directly to GitHub Pages.

Support
=======
You can ask questions by sending emails to adviser-support@ims.uni-stuttgart.de.

You can also post bug reports and feature requests in GitHub issues.

.. _home:how_to_cite:

How to cite
===========
If you use or reimplement any of this source code, please cite the following paper:

.. code-block:: bibtex

   @InProceedings{
    title =     {ADVISER: A Toolkit for Developing Multi-modal, Multi-domain and Socially-engaged Conversational Agents},
    author =    {Chia-Yu Li and Daniel Ortega and Dirk V{\"{a}}th and Florian Lux and Lindsey Vanderlyn and Maximilian Schmidt and Michael Neumann and Moritz V{\"{o}}lkel and Pavel Denisov and Sabrina Jenne and Zorica Karacevic and Ngoc Thang Vu},
    booktitle = {Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020) - System Demonstrations},
    publisher = {Association for Computational Linguistics},
    location =  {Seattle, Washington, USA},
    year =      {2020}
    }

License
=======
Adviser is published under the GNU GPL 3 license.
