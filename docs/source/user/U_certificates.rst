Certificates
============

Before any communtication is done with the KMEs, a client needs to have the proper certificates to do mutual TLS authentication. 
Every certificate comes with the corresponding key and the CA chain of the certificate. There are several way to implement this.

Private Keys
------------   

To be able to use Guardian, the SAE needs a minimium of at least a XXX key length for RSA and xxx key length for EC-type. In the future, once TLS 1.2 is depreciated, only EC-type keys are allowed.

Certificate Signing Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the private key, a certificate signing request is must be issued with the correct identifiers that bind the key/certificate to the SAE. The mandatory identifiers are


   #. Country
   
   #. State

   #. Locality
   
   #. Organisation Unit
   
   #. Common Name
   
Optional identifiers are
   
   #. Blah
   
   #. Blah
   
The CSR is then handed over to the |QKDdc| who will sign it and return a certificate together with the CA chain for the SAE to use.


.. |QKDdc| replace:: QKD device controller
.. _`QKDdc`: :ref:`QKD controller`

Private key/certificate generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a client (SAE) doesn't have a private key, and will need one anyway, the |QKDdc| can generate a key and certificate pair and hand it over to the client. The drawback of this method is that the |QKDdc| will know the private key too. 


Certificate Authority Chain
---------------------------

If the certificate that the client uses was signed by the intermediate CA residing in the KME that it wants to communicate with, then the client can already communicate with the KME.
However sometimes, there may be lots of clients that already have their certificates signed by a different trusted Certificate Authority and it may be a hassle for all of them to issue another CSR to be signed by the |QKDdc|.
In this case, the client may give his/her CA chain to the |QKDdc| to be included in the list of trusted root CA.
If the |QKDdc| decides that the CA chain is trustworthy and includes it as a trustworthy root CA, the client will now have access to the KME. 

