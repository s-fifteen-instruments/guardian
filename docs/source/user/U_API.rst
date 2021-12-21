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
^^^^^^^^^^^

Check Vconn is an endpoint that returns to the client the 
connection status to the Vault running on the KME. 
No parameters are sent.

The response body is

.. code:: json
   
   {
      "is_initialized": "bool",
      "is_sealed": "bool",
      "is_authenticated": "bool"
   }
   

Example Value
   

.. code:: json
   
   {
      "is_initialized": "true",
      "is_sealed": "false",
      "is_authenticated": "true"
   }
   
   
Get Status
^^^^^^^^^^

Get status is the endpoint where the client can verify if the connection to another SAE exists and also keying materials size limits and counts.

The parameters are sent via a GET access method with  ``KME_hostname`` and ``slave_SAE_ID`` encoded in the access URL.

Example request URL
   ``https://kme1/api/v1/keys/sae3/status``
   

The Response body is

.. code:: json

   {
     "source_KME_ID": "kme1",
     "target_KME_ID": "kme2",
     "master_SAE_ID": "string",
     "slave_SAE_ID": "string",
     "key_size": 32,
     "stored_key_count": 1048576,
     "max_key_count": 1048576,
     "max_key_per_request": 100,
     "max_key_size": 65536,
     "min_key_size": 8,
     "max_SAE_ID_count": 0,
     "status_extension": {
       "status_extension": "string"
     }
   }
   
Example Value for success

.. code:: json

   }
     "source_KME_ID": "kme1",
     "target_KME_ID": "kme2",
     "master_SAE_ID": "sae1",
     "slave_SAE_ID": "sae4",
     "key_size": 32,
     "stored_key_count": 1150,
     "max_key_count": 1048576,
     "max_key_per_request": 100,
     "max_key_size": 65536,
     "min_key_size": 8,
     "max_SAE_ID_count": 0
   }
   
.. For Failure   
   
Get key
^^^^^^^

Get key is called by the master SAE with the slave SAE_id and optional number of keys and size. The source KME will negotiate with the target KME where the slave SAE resides to generate symmetric keys encoded in **base64** for the master and slave SAEs 

Parameters are sent via a GET access method with ``KME_hostname`` and ``slave_SAE_ID`` encoded in the access URL. Optional parameters ``numbers`` and ``size`` will default to 1 and 32 (bits) if unspecified.

Example request URL
   ``https://kme1/api/v1/keys/sae2/enc_keys?number=2&size=24``

The response body is

.. code:: json
   
   {
     "key_container_extension": "string",
     "keys": [
       {
         "key_extension": "string",
         "key": "string",
         "key_ID_extension": "string",
         "key_ID": "stringstringstri"
       }
     ]
   }   
   
with options ``key_container_extension``, ``key_extension`` and ``key_ID_extension`` defined for future use.
   
Example Value for success

.. code:: json

   {
     "keys": [
       {
         "key": "2Azd",
         "key_ID": "a6c4048f-a9ff-5661-b281-9d4ab9893dff"
       },
       {
         "key": "BUl7",
         "key_ID": "296a7e8e-fcde-5539-aaee-92e629d169d0"
       }
     ]
   }


Post key
^^^^^^^^


Get Key With Key Ids
^^^^^^^^^^^^^^^^^^^^


Post Key With Key Ids
^^^^^^^^^^^^^^^^^^^^^


HTTP Error Codes
----------------

All APIs except for Check Vconn may return the following responses.

==================   ======================  ======================
HTTP status code     Response data model     Description
==================   ======================  ======================
200                  Success                 Successful Response.
400                  Error                   Bad request format.
401                  -                       Unauthorized.
422                  Error                   Validation Error.
503                  Error                   Error on Server side.
==================   ======================  ======================

