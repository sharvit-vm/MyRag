# L3 RCA Test Errors

Use these intentional Java runtime bugs to test L3 RCA after copying this folder into the `MyRag` repo.

## 1. Small Error - Null Email Lookup

File:

```text
Insurance-Management-System/src/main/java/com/vinay/service/ClientServiceImpl.java
```

Buggy method:

```text
findByEmail
```

Trigger:

```text
Call the client lookup flow with a missing/null email value.
```

Expected stack trace shape:

```text
java.lang.NullPointerException: Cannot invoke "String.trim()" because "email" is null
    at com.vinay.service.ClientServiceImpl.findByEmail(ClientServiceImpl.java:49)
    at com.vinay.controller.ClientController.getClientByEmail(ClientController.java:57)
```

Expected RCA:

```text
The method normalizes email using email.trim() without validating that email is present.
```

## 2. Medium Error - Password Update Null Check Missing

File:

```text
Insurance-Management-System/src/main/java/com/vinay/service/ClientServiceImpl.java
```

Buggy method:

```text
updateClientInfo
```

Trigger:

```text
Update a client without sending password in the request body.
```

Expected stack trace shape:

```text
java.lang.NullPointerException: Cannot invoke "String.length()" because the return value of "com.vinay.dto.ClientDto.getPassword()" is null
    at com.vinay.service.ClientServiceImpl.updateClientInfo(ClientServiceImpl.java:73)
    at com.vinay.controller.ClientController.updateClient(ClientController.java:41)
```

Expected RCA:

```text
The update flow assumes password is always present and calls client.getPassword().length() without a null check.
```

## 3. Medium Error - Claim Policy Null Dereference

File:

```text
Insurance-Management-System/src/main/java/com/vinay/service/ClaimServiceImpl.java
```

Buggy method:

```text
createNewClaim
```

Trigger:

```text
Create a claim using /claim/{id} but do not include a nested policy object in the request body.
```

Expected stack trace shape:

```text
java.lang.NullPointerException: Cannot invoke "com.vinay.dto.InsurancePolicyDto.getId()" because the return value of "com.vinay.dto.ClaimDto.getPolicy()" is null
    at com.vinay.service.ClaimServiceImpl.createNewClaim(ClaimServiceImpl.java:43)
    at com.vinay.controller.ClaimController.createClaim(ClaimController.java:37)
```

Expected RCA:

```text
The controller already passes policyId as a path variable, but the service also dereferences claim.getPolicy().getId() before setting the policy on the claim DTO.
```
