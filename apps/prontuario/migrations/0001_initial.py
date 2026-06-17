# Generated for the MedClinic Módulo de Prontuário Eletrônico.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prontuario',
            fields=[
                ('idProntuario', models.AutoField(db_column='idProntuario', primary_key=True, serialize=False)),
                ('dataCriacao', models.DateTimeField(auto_now_add=True, db_column='dataCriacao')),
                ('diagnostico', models.TextField(blank=True, default='')),
                ('observacoes', models.TextField(blank=True, default='')),
                ('historicoEvolucoes', models.TextField(blank=True, db_column='historicoEvolucoes', default='')),
                ('prescricaoAtiva', models.TextField(blank=True, db_column='prescricaoAtiva', default='')),
            ],
            options={
                'verbose_name': 'Prontuário',
                'verbose_name_plural': 'Prontuários',
                'db_table': 'Prontuario',
                'ordering': ['-idProntuario'],
            },
        ),
        migrations.CreateModel(
            name='MedicoProntuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idMedico', models.IntegerField(db_column='idMedico')),
                ('prontuario', models.ForeignKey(db_column='idProntuario', on_delete=django.db.models.deletion.CASCADE, related_name='medicos_autorizados', to='prontuario.prontuario')),
            ],
            options={
                'verbose_name': 'Acesso de médico ao prontuário',
                'verbose_name_plural': 'Acessos de médicos aos prontuários',
                'db_table': 'Medico_Prontuario',
                'unique_together': {('idMedico', 'prontuario')},
            },
        ),
        migrations.CreateModel(
            name='EnfermeiroProntuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idEnfermeiro', models.IntegerField(db_column='idEnfermeiro')),
                ('prontuario', models.ForeignKey(db_column='idProntuario', on_delete=django.db.models.deletion.CASCADE, related_name='enfermeiros_autorizados', to='prontuario.prontuario')),
            ],
            options={
                'verbose_name': 'Acesso de enfermeiro ao prontuário',
                'verbose_name_plural': 'Acessos de enfermeiros aos prontuários',
                'db_table': 'Enfermeiro_Prontuario',
                'unique_together': {('idEnfermeiro', 'prontuario')},
            },
        ),
        migrations.CreateModel(
            name='FarmaceuticoProntuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idFarmaceutico', models.IntegerField(db_column='idFarmaceutico')),
                ('prontuario', models.ForeignKey(db_column='idProntuario', on_delete=django.db.models.deletion.CASCADE, related_name='farmaceuticos_autorizados', to='prontuario.prontuario')),
            ],
            options={
                'verbose_name': 'Acesso de farmacêutico ao prontuário',
                'verbose_name_plural': 'Acessos de farmacêuticos aos prontuários',
                'db_table': 'Farmaceutico_Prontuario',
                'unique_together': {('idFarmaceutico', 'prontuario')},
            },
        ),
    ]
