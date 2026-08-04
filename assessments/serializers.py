# assessments/serializers.py
from rest_framework import serializers
from .models import SelfAssessment


class SelfAssessmentSerializer(serializers.ModelSerializer):
    # Adjust field names ('name' or 'title') to match your subjects.Subject model
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SelfAssessment
        fields = [
            'id',
            'student',
            'subject',
            'subject_code',
            'subject_name',
            'strength_score',
            'weakness_score',
            'updated_at',
        ]
        read_only_fields = ['id', 'student', 'updated_at']

    def create(self, validated_data):
        """
        Ensures US-04 requirement: resubmitting updates an existing score 
        for the student-subject pair rather than raising an integrity error.
        """
        request = self.context.get('request')
        student = request.user
        subject = validated_data.get('subject')

        assessment, _ = SelfAssessment.objects.update_or_create(
            student=student,
            subject=subject,
            defaults={
                'strength_score': validated_data.get('strength_score'),
                'weakness_score': validated_data.get('weakness_score'),
            }
        )
        return assessment


class BulkSelfAssessmentSerializer(serializers.Serializer):
    """
    Serializer to handle submitting/updating ratings for multiple subjects at once.
    """
    assessments = SelfAssessmentSerializer(many=True)

    def create(self, validated_data):
        request = self.context.get('request')
        student = request.user
        assessments_data = validated_data.get('assessments', [])

        saved_assessments = []
        for item in assessments_data:
            assessment, _ = SelfAssessment.objects.update_or_create(
                student=student,
                subject=item['subject'],
                defaults={
                    'strength_score': item['strength_score'],
                    'weakness_score': item['weakness_score'],
                }
            )
            saved_assessments.append(assessment)

        return saved_assessments