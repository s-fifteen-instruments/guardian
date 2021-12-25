Overview
========

.. _`QKD controller`:

The |QKDdc| has a dual role is establishing QKD links between KMEs and also authorising SAEs onto which KME they can communicate to. In the initial implementation, only two nodes are present and thus the |QKDdc| in only responsible for stopping and starting the devices which is described in `QKDServer <https://github.com/s-fifteen-instruments/QKDServer/>`_.

.. |QKDdc| replace:: QKD device controller


Unsealing Vault
---------------

Whenever the Vault is started, it is in a sealed state. It will also be the |QKDdc|'s duty together to unseal the vault. He/she will need a minimum quorum of unseal keys in order to do this.

.. figure:: ./images/vault_sealed.png
   :alt: Vault in a sealed state

.. figure:: ./images/vault_unseal_1.png
   :alt: One unseal key entered
   
.. figure:: ./images/vault_unseal_2.png
   :alt: Two unseal keys entered

.. figure:: ./images/vault_login.png
   :alt: Vault unsealed

