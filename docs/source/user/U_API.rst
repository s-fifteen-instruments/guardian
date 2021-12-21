Application Programming Interface
=================================

.. _api:

The APIs that are available to the client (SAEs) 

   +------------------------+----------------------------+
   | Method name            |   defined path             |
   +------------------------+----------------------------+
   | Check Vconn            | /api/v1/check_vconn/       |
   +------------------------+----------------------------+
   | Get status             | /api/v1/keys/sae_id/status |
   +------------------------+----------------------------+
   | Get key                |/api/v1/keys/sae_id/enc_keys|
   +------------------------+----------------------------+
   | Post key               |/api/v1/keys/sae_id/enc_keys|
   +------------------------+----------------------------+
   | Get Key With Key Ids   |/api/v1/keys/sae_id/dec_keys|
   +------------------------+----------------------------+
   | Post Key With Key Ids  |/api/v1/keys/sae_id/dec_keys|
   +------------------------+----------------------------+
   

Check Vconn
-----------

Check Vconn is an endpoint that returns to the client the 
connection status to the Vault running on the KME. 
No parameters are sent.

   The response body is

.. code:: json
   
   {
      "is_initialized": bool,
      "is_sealed": bool,
      "is_authenticated": bool
   }
   

   Example Value
   

.. code:: json
   
   {
      "is_initialized": true,
      "is_sealed": false,
      "is_authenticated": true
   }
   
   
Get Status
----------

Get status is the endpoint where the client can verify the 


Get key
-------


Post key
--------


Get Key With Key Ids
--------------------


Post Key With Key Ids
---------------------