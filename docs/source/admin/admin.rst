Administrating
==============

Under normal circumstances, the |admin| does not need to do anything once the system is set up. Things that the |admin| have to do includes 

#. creating additional entities in Vault such as |QKDdc|.

#. Adding additional trusted CA chains of client in ``traefik``


Adding additional |QKDdc| in Vault
----------------------------------

To be documented..


Traefik TLS configuration 
-------------------------

.. TODO: Park the bottom section under |admin| sections instead.

This authentication can be performed with different granularity levels:

   - Installation of root CA certificate (not recommended)
   - Installation of intermediate CA certificate chain - appropriate for bulk authentication of SAEs that belong to the same organization
   - Installation of client certificate chain - only the single client certificate is authenticated

.. warning::

   This method unconditionally authenticates all SAEs that belong to the installed certificate chain, which can introduce a potential security risk. Additional measures such as X.509 extended attributes may be utilized to distinguish clients.

The configuration file can be found under `tls.yml <https://github.com/s-fifteen-instruments/guardian/blob/main/volumes/kme1/traefik/configuration/traefik.d/tls.yml>`_ 

::
   
   # Traefik dynamic configuration file
   # Specifically for TLS settings
   .
   .
   .
   .
      clientAuth:
        caFiles:
        # Allow clients from both KME CA chains
        - /certificates/{{ env "LOCAL_KME_ID" }}/rest/rest.ca-chain.cert.pem
        - /certificates/{{ env "REMOTE_KME_ID" }}/rest/rest.ca-chain.cert.pem
        # Allow only local SAE client CA chain
        - /certificates/{{ env "LOCAL_KME_ID" }}/{{ env "LOCAL_SAE_ID" }}/{{ env "LOCAL_SAE_ID" }}.ca-chain.cert.pem
        # Add additional trusted CA Chains
        # - /certificates/other-trusted-root-ca.cert.pem
        # - /certificates/other-trusted-int-ca.cert.pem
        # - /certificates/trusted-client-ca.cert.pem
        clientAuthType: RequireAndVerifyClientCert
   .
   .
   .

This is a dynamic configuration file meaning that Traefik will automatically update the TLS configurations without having to be brought down and up again.

.. |QKDdc| replace:: QKD device controller

   
.. |admin| replace:: Administrator
