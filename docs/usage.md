## Usage
Here is a collection of examples on how to use certain functions, such as what argument has to be passed, and from where the information came from.

```python
infos = user.getEvaluationSettings()
info = user.getEvaluation(infos[0]["periods"][0]["id"])
```

```python
infos = user.getAgenda('2024-11-25', '2024-11-25')
info = user.getLesson(infos[0]["lessons"][0]["id"])
```

```python
infos = user.getHomeworkAssignments('2024-11-26', '2024-11-27')
info = user.patchHomeworkAssignment(infos[0]["id"], {"done": True})
```

```python
total_infos = user.getUsersMailSettings()
infos = user.getCommunicationsFolder(total_infos["folders"][1]["id"])
info = user.getCommunication(infos[3]["id"])
```

```python
total_infos = user.getUsersMailSettings()
infos = user.getCommunicationsFolder(total_infos["folders"][0]["id"])
info = user.getCommunicationParticipations(infos[0]["id"])
```

```python
total_infos = user.getUsersMailSettings()
infos = user.getCommunicationsFolder(total_infos["folders"][0]["id"])
info = user.getCommunicationParticipants(infos[0]["id"])
```

```python
total_infos = user.getUsersMailSettings()
infos = user.getCommunicationsFolder(total_infos["folders"][0]["id"])
info = user.patchCommunicationFolders(infos[7]["id"], total_infos["folders"])
```
