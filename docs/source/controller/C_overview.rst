Overview
========

.. _`QKD controller`:

The |QKDdc| has a dual role is establishing QKD links between KMEs and also authorising SAEs onto which KME they can communicate to. In the initial implementation, only two nodes are present and thus the |QKDdc| is only responsible for stopping and starting the devices which is described in `QKDServer <https://github.com/s-fifteen-instruments/QKDServer/>`_. 

The |QKDdc| may also be responsible for unsealing the vault depending on how strict the implementation of the QKD device is configured. In the current [#]_ Guardian implementation, there is an ``unsealer`` process that does this automatically.


.. |QKDdc| replace:: QKD device controller

.. [#] Version |version|

Unsealing Vault
---------------

Whenever the Vault is started, it is in a sealed state. It will also be the |QKDdc|'s duty together to unseal the vault (if implemented as such). He/she will need a minimum quorum of unseal keys in order to do this.


GUI
^^^

.. figure:: ./images/vault_sealed.png
   :alt: Vault in a sealed state

   When Vault is in a sealed state, the Vault GUI interface will indicate with a red sealed under status. It will display the following prompt for the Unseal Key Portion to be entered.

.. figure:: ./images/vault_unseal_1.png
   :alt: One unseal key entered
   
   If one unseal key is entered, it shows 1/3 keys provided.
   
.. figure:: ./images/vault_unseal_2.png
   :alt: Two unseal keys entered
   
   Similarly for two unseal keys entered.

.. figure:: ./images/vault_login.png
   :alt: Vault unsealed
   
   Once the vault is unsealed, the login screen is shown once again with the status now green indicating that Vault is unsealed.

----

API
^^^

Vault also has an API endpoint for the unsealing process. This is documented in `Vault documentation <https://www.vaultproject.io/api-docs/system/unseal>`_.
Briefly, it supplies a PUT request to `/sys/unseal` with a JSON payload of the unseal key.

.. tabs::

   .. group-tab:: Sample Payload

      .. code:: json
        
         {
            "key": "abcd1234..."
         }

    
   .. group-tab:: Sample Request

      .. code:: shell-session
        
         $ curl \
             --request PUT \
             --data @payload.json \
             --key key.pem \
             --cert cert.pem \
             --cacert cacert.pem \
             http://kme_id:8200/v1/sys/unseal

----


HVAC
^^^^

If using Python, the ``hvac`` module has the `submit_unseal_key(key=None, reset=False, migrate=False) <https://hvac.readthedocs.io/en/stable/usage/system_backend/seal.html?highlight=unseal#submit-unseal-key>`_ function. This is the same function that Guardian's ``unsealer`` uses.

In essence, this function makes use of the Vault API ``/v1/sys/unseal`` backend to input the unseal keys.
