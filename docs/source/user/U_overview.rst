Overview
========

Guardian follows ETSI GS QKD 014 specification which aims to make it simple and easy for developers to understand. It's REST-based APIs uses data encoded in the JSON format to deliver block keys with key IDs to applications. This simplicity allows ease of implementation in a scalable way.

The goal of this Guardian is to implement a simple request and response style API between an SAE (Secure Application Entity) and a KME (Key Management Entity). SAEs request keys from KMEs which then deliver them to the SAE.
SAEs are intended to have secure access to the KME they are connecting to. This API doesn’t handle the secure key generation and distribution by the QKD technology. What it does instead is to accept and secure the generated key for delivery to any SAE that makes a key request.

Before using Guardian, several prerequisites are needed.

   1. A key-certificate pair that is trusted by and compatible with the local KME.
   2. The root CA certificate that signed the local KME certificate together with the revocation list.
   3. A TLS v1.2 enabled functions/programs that can make HTTPs GET/POST calls and understand JSON data encoding.
   4. A corresponding SAE client on another remote KME that also has items 1-3 on their end.
   5. A connection between the local KME and the remote KME.

Once setup, the SAE can make a connection to the local KME and make the API calls.
These calls can be found in :ref:`API`.
Communication between SAEs to do share their keyIDs are handled by the Users and not the scope of the API.
 
