Administrator Overview
======================

In normal operation, the users and Controllers can only access Guardian via the Web interface and/or APIs defined. No user is allowed to log in to the operating system except for the Administrator.

Thus the administrator's duty is to configure the settings, users and access policy for the QKD system.

Two Nodes
---------

In the two node configuration, there can only be one local and one remote.
As such, it is assumed that the slave client is connected to the remote KME by default.
Setup for such two nodes is relatively straight forward.
This is explained in :ref:`Setting Up`. 

As of version |version|, this is the default implementation. 

Three Nodes
-----------

In a three node configuration, there are now two remote parties for every local node. Setting up such a system is a bit more involved since there are now three two node connections that needs to be established.

The setting up of the three node configuration is still being finalised and not implemented yet in version 0.7.0


Controllers and clients
-----------------------

The administrator will need to set up the certificates and/or user/passwords for |QKDdc| to access the PKI engine and also operate the QKD software. If the |QKDdc| are also responsible for :ref:`unsealing vault <unsealing Vault>`, then it is important that a quorum of |QKDdc| are set up. This is because the unseal keys can also be used to set up a new `root token <https://www.vaultproject.io/docs/concepts/tokens#root-tokens>`_ which has unlimited access to Vault.

The administrator can also add external CA chains that clients can use to authenticate themselves to Guardian. The |QKDdc| cannot do this since it requires access to the operating system filesystem, specifically,  :ref:`tls.yml <dynamic_tls>`

Although the client can access the Vault UI with his/her certificate, his/her credentials doesn't allow login via TLS. The client can only interact with Guardian.

Access Control Policies
^^^^^^^^^^^^^^^^^^^^^^^

A proper segmentation of roles is implemented by the ACL policy in Vault. Right now, there are only three additional policies other than the default one. These are

#. ``int_ca_cert_issuer`` for issuing and signing certificates on the pki secrets engine resides in Vault.
#. ``rest`` where Guardian interacts with Vault to access the QKD secret keys.
#. ``watcher`` which ingests the keys from the QKD device into the Vault.

These policies exist in the `vault policies <https://github.com/s-fifteen-instruments/guardian/tree/main/volumes/kme1/vault/policies/>`_ directory



.. |QKDdc| replace:: QKD device controller
