### getUserInfo()
```json
"params" : {
  "fields": {
    "userInfo": "lastName,firstName,photoUrl,externalMail,mobilephone,permissions",
    "school": "name,timeZone,subscribedServices",
    "legalRepresentativeUserInfo": "addressLines,postalCode,city,country,students",
    "studentUserInfo": "className,dateOfBirth,regime,school",
    "student": "firstName,lastName,photoUrl,className,dateOfBirth,regime,school"
  }
}
```

### getEvaluationSettings()
```json
"params" : {
  "fields": {
    "evaluationsSetting": "periodicReportsEnabled,skillsEnabled,evaluationsDetailsAvailable",
    "period": "label,startDate,endDate",
    "skillsSetting": "skillAcquisitionLevels,skillAcquisitionColors",
    "skillAcquisitionColors": "colorLevelMappings"
  }
}
```

### getEvaluation()
```json
"params" : {
  "fields": {
    "evaluationService": "coefficient,average,studentAverage,scale",
    "subject": "label,color",
    "evaluation": "dateTime,coefficient,average,scale,evaluationResult,subSkills",
    "evaluationResult": "mark,nonEvaluationReason,subSkillsEvaluationResults",
    "subSkillEvaluationResult": "level,subSkill",
    "teacher": "firstName,lastName,title",
    "subSkill": "shortLabel"
  }
}
```

### getEvaluationDetail()
```json
"params" : {
  "fields": {
    "evaluationService": "subject,teachers",
    "subject": "label,color",
    "subSubject": "label",
    "evaluation": "title,topic,dateTime,coefficient,min,max,average,scale",
    "evaluationResult": "subSkillsEvaluationResults,nonEvaluationReason,mark,comment",
    "subSkill": "shortLabel",
    "subSkillEvaluationResult": "level,subSkill",
    "teacher": "firstName,lastName,title"
  }
}
```

### getPeriodicReportsFiles()
```json
"params" : {
  "fields": {
    "periodicReportFile": "name,mimeType,size,url,mimeTypeLabel"
  }
}
```

### getAgenda()
```json
"params" : {
  "fields": {
    "lesson": "title,startDateTime,endDateTime,location,canceled,subject,teachers",
    "homework": "title,done,dueDateTime,subject",
    "cateringService": "title,startDateTime,endDateTime",
    "teacher": "firstName,lastName,title",
    "subject": "label,color"
  }
}
```

### getUsersMailSettings()
```json
"params" : {
  "fields": {
    "personContact": "person,linksWithUser",
    "groupContact": "label,personContacts,linksWithUser",
    "person": "firstName,lastName,title,photoUrl",
    "userMailSetting": "maxCharsInParticipationContent,maxCharsInCommunicationSubject",
    "signature": "content",
    "folder": "name,position,type,parent"
  }
}
```