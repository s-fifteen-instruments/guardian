.. _api:

Application Programming Interface
=================================

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
     "key_size": "integer",
     "stored_key_count": "integer",
     "max_key_count": "integer",
     "max_key_per_request": "integer",
     "max_key_size": "integer",
     "min_key_size": "integer",
     "max_SAE_ID_count": "integer",
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

Get key is called by the master SAE with the slave SAE_id and optional number of keys and size. The source KME will negotiate with the target KME where the slave SAE resides to generate symmetric keys encoded in `**base64**`__ for the master and slave SAEs 

.. __: https://www.rfc-editor.org/info/rfc4648

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
         "key_ID": "string"
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

Similar to Get Key, but with a Post access method instead. With this method, the SAE may specify additional options of ``additional_slave_SAE_IDs``, ``extension_mandatory`` and ``extension_optional`` in the request. These however are not implement by Guardian.

Example request URL
   ``https://kme1/api/v1/keys/sae2/enc_keys``
   
The request body is 

.. code:: json

   {
     "number": 1,
     "size": 32,
     "additional_slave_SAE_IDs": [],
     "extension_mandatory": [
       {}
     ],
     "extension_optional": [
       {}
     ]
   }

The response body is the same as Get Key

.. code:: json
   
   {
     "key_container_extension": "string",
     "keys": [
       {
         "key_extension": "string",
         "key": "string",
         "key_ID_extension": "string",
         "key_ID": "string"
       }
     ]
   }   
   
   
Get Key With Key Ids
^^^^^^^^^^^^^^^^^^^^

This method is called by the Slave SAE on his/her target KME. It retrives the matching key from the KME through the use of the Key Id(s) that the master SAE notified the Slave SAE.

Example request URL
   ``https://kme2/api/v1/keys/sae1/dec_keys?key_ID=ce9d2863-d4f8-522d-aa5a-95fcd1320648``

The response body is the also the same as Get Key and Post Key

.. code:: json
   
   {
     "key_container_extension": "string",
     "keys": [
       {
         "key_extension": "string",
         "key": "string",
         "key_ID_extension": "string",
         "key_ID": "string"
       }
     ]
   }   
   

Post Key With Key Ids
^^^^^^^^^^^^^^^^^^^^^

If more than one Key needs to be retrived from multiple Key Ids, then the Post method is used.

Example request URL
   ``https://kme2/api/v1/keys/sae1/dec_keys``
   
The request body is the same as 

.. code:: json

   {
     "key_IDs_extension": "string",
     "key_IDs": [
       {
         "key_ID_extension": "string",
         "key_ID": "string"
       }
     ]
   }

Example request body,

.. code:: json

   {
     "key_IDs_extension": "string",
     "key_IDs": [
       {
         "key_ID_extension": "",
         "key_ID": "f1f13be6-fc07-58d8-bd44-aabad86a4dc1"
       },
       {
         "key_ID_extension": "",
         "key_ID": "0e21abe7-1679-5832-82a6-fd27cff4a653"
       }
     ]
   }

The Response body is again the same as that for Get Key, Post key and Get key with Key Id


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

