.. _api:

Application Programming Interface
=================================

The API endpoints that are available to the client (SAEs) is summarized in the table below:

=======================================  ================
Actions                                  Endpoint
=======================================  ================
`Check vault connection`_                /check_vconn
`Get SAE status`_                        /keys/sae_id/status
`Retrieve new keys`_                     /keys/sae_id/enc_keys
`Retrieve new keys with extensions`_     /keys/sae_id/enc_keys
`Retrieve key from key ID`_              /keys/sae_id/dec_keys
`Retrieve multiple keys from key IDs`_   /keys/sae_id/dec_keys
=======================================  ================

In the examples below, we denote the KME domain ``https://kme1/`` and current sae ``sae1``.

----

Check vault connection
----------------------

Checks the connection status of the SAE to the Vault running on the KME.  
No parameters are sent.

+--------------+------------------------------------------+
| **Method:**  | GET                                      |
+--------------+------------------------------------------+
| **Format:**  | ``/check_vconn``                         |
+--------------+------------------------------------------+
| **Example:** | ``https://kme1/api/v1/check_vconn``      |
+--------------+------------------------------------------+

.. tabs::

   .. group-tab:: Response schema

      .. code:: json
        
        {
            "is_initialized": "bool",
            "is_sealed": "bool",
            "is_authenticated": "bool"
        }
    
   .. group-tab:: Example successful response

      .. code:: json
        
        {
            "is_initialized": true,
            "is_sealed": false,
            "is_authenticated": true
        }

----

Get SAE status
--------------

Verifies if a connection to another SAE exists. If so, return the keying material size limits and counts.  
The parameters are sent via a GET access method with ``slave_SAE_ID`` encoded in the access URL.

+--------------+------------------------------------------+
| **Method:**  | GET                                      |
+--------------+------------------------------------------+
| **Format:**  | ``/keys/{slave_SAE_ID}/status``          |
+--------------+------------------------------------------+
| **Example:** | ``https://kme1/api/v1/keys/sae3/status`` |
+--------------+------------------------------------------+
   
.. tabs::

   .. group-tab:: Response schema

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
    
   .. group-tab:: Example successful response

      .. code:: json

        {
          "source_KME_ID": "kme1",
          "target_KME_ID": "kme2",
          "master_SAE_ID": "sae1",
          "slave_SAE_ID": "sae3",
          "key_size": 32,
          "stored_key_count": 1150,
          "max_key_count": 1048576,
          "max_key_per_request": 100,
          "max_key_size": 65536,
          "min_key_size": 8,
          "max_SAE_ID_count": 0
        }

----

Retrieve new keys
-----------------

Called by the master SAE with the slave ``SAE_id`` and optional number of keys and size. The source KME will negotiate with the target KME where the slave SAE resides to generate symmetric keys encoded in `base64 <https://www.rfc-editor.org/info/rfc4648>`_ for the master and slave SAEs.

Parameters are sent via a GET access method with ``KME_hostname`` and ``slave_SAE_ID`` encoded in the access URL. Optional parameters ``numbers`` and ``size`` will default to 1 and 32 (bits) if unspecified.

+--------------+-------------------------------------------------------------+
| **Method:**  | GET                                                         |
+--------------+-------------------------------------------------------------+
| **Format:**  | ``/keys/{slave_SAE_ID}/enc_keys``                           |
+--------------+-------------------------------------------------------------+
| **Example:** | ``https://kme1/api/v1/keys/sae2/enc_keys?number=2&size=24`` |
+--------------+-------------------------------------------------------------+

.. tabs::

   .. group-tab:: Response schema

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
    
   .. group-tab:: Example successful response

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

----

Retrieve new keys with extensions
---------------------------------

Similar to `Retrieve new keys`_, but with a POST access method instead. With this method, the SAE may specify additional options of ``additional_slave_SAE_IDs``, ``extension_mandatory`` and ``extension_optional`` in the request. These are currently not implemented by Guardian.

+--------------+-------------------------------------------------------------+
| **Method:**  | POST                                                        |
+--------------+-------------------------------------------------------------+
| **Format:**  | ``/keys/{slave_SAE_ID}/enc_keys``                           |
+--------------+-------------------------------------------------------------+
| **Example:** | ``https://kme1/api/v1/keys/sae2/enc_keys``                  |
+--------------+-------------------------------------------------------------+

Request body:

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

The response body is the same as `Retrieve new keys`_.

----

Retrieve key from key ID
------------------------

Retrives the matching key from the KME through the use of the Key ID(s) that the master SAE notified the Slave SAE. This method is called by the Slave SAE on his/her target KME.

+--------------+----------------------------------------------------------------------------------------+
| **Method:**  | GET                                                                                    |
+--------------+----------------------------------------------------------------------------------------+
| **Format:**  | ``/keys/{master_SAE_ID}/dec_keys``                                                     |
+--------------+----------------------------------------------------------------------------------------+
| **Example:** | ``https://kme1/api/v1/keys/sae1/dec_keys?key_ID=ce9d2863-d4f8-522d-aa5a-95fcd1320648`` |
+--------------+----------------------------------------------------------------------------------------+

The response body is the also the same as that of `Retrieve new keys`_ and `Retrieve new keys with extensions`_.

----

Retrieve multiple keys from key IDs
-----------------------------------

Retrieves one or more keys from the KME by specifying one or more key IDs.

+--------------+--------------------------------------------+
| **Method:**  | POST                                       |
+--------------+--------------------------------------------+
| **Format:**  | ``/keys/{master_SAE_ID}/dec_keys``         |
+--------------+--------------------------------------------+
| **Example:** | ``https://kme1/api/v1/keys/sae1/dec_keys`` |
+--------------+--------------------------------------------+
   
Request body:

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

Request body example:

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

The response body is again the same as that for `Retrieve new keys`_, `Retrieve new keys with extensions`_ and `Retrieve key from key ID`_.

----

HTTP Error Codes
----------------

All endpoints except for `Check vault connection`_ may return the following responses.

==================   ======================  ======================
HTTP status code     Response data model     Description
==================   ======================  ======================
200                  Success                 Successful Response
400                  Error                   Bad request format
401                  `-`                     Unauthorized
422                  Error                   Validation Error
503                  Error                   Error on Server side
==================   ======================  ======================
