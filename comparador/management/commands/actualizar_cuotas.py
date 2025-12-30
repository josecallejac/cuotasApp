from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from comparador.models import CasaApuestas, Deporte, Evento, TipoCuota, Cuota


class Command(BaseCommand):
    help = 'Actualiza las cuotas de apuestas de forma simulada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta en modo de prueba sin guardar cambios',
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Número de días de eventos a actualizar (por defecto: 7)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dias = options['dias']

        self.stdout.write(
            self.style.SUCCESS(f'Actualizando cuotas para próximos {dias} días...')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO PRUEBA: No se guardarán cambios en la base de datos')
            )

        # Obtener eventos activos
        fecha_limite = timezone.now() + timedelta(days=dias)
        eventos = Evento.objects.filter(
            finalizado=False,
            fecha_evento__lte=fecha_limite,
            fecha_evento__gte=timezone.now()
        ).select_related('deporte')

        if not eventos.exists():
            self.stdout.write(
                self.style.WARNING('No hay eventos activos para actualizar')
            )
            return

        total_actualizaciones = 0

        for evento in eventos:
            actualizaciones_evento = self.actualizar_cuotas_evento(evento, dry_run)
            total_actualizaciones += actualizaciones_evento

            if actualizaciones_evento > 0:
                self.stdout.write(
                    f'✓ {evento}: {actualizaciones_evento} cuotas actualizadas'
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'PRUEBA COMPLETADA: {total_actualizaciones} cuotas serían actualizadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'ACTUALIZACIÓN COMPLETADA: {total_actualizaciones} cuotas actualizadas')
            )

    def actualizar_cuotas_evento(self, evento, dry_run=False):
        """Actualiza las cuotas de un evento específico"""
        actualizaciones = 0

        # Obtener cuotas existentes del evento
        cuotas_existentes = Cuota.objects.filter(evento=evento)

        if not cuotas_existentes.exists():
            # Si no hay cuotas, crear algunas básicas
            actualizaciones += self.crear_cuotas_iniciales(evento, dry_run)
        else:
            # Actualizar cuotas existentes
            for cuota in cuotas_existentes:
                if self.actualizar_cuota_individual(cuota, dry_run):
                    actualizaciones += 1

        return actualizaciones

    def crear_cuotas_iniciales(self, evento, dry_run=False):
        """Crea cuotas iniciales para un evento nuevo"""
        creaciones = 0

        # Obtener casas de apuestas activas
        casas = CasaApuestas.objects.filter(activa=True)
        if not casas.exists():
            return creaciones

        # Obtener tipos de cuota disponibles
        tipos_cuota = TipoCuota.objects.all()
        if not tipos_cuota.exists():
            return creaciones

        for tipo_cuota in tipos_cuota:
            opciones = self.obtener_opciones_por_tipo(tipo_cuota)

            for opcion in opciones:
                # Crear cuota para cada casa de apuestas
                for casa in casas:
                    cuota_valor = self.generar_cuota_base(tipo_cuota)

                    if not dry_run:
                        Cuota.objects.create(
                            evento=evento,
                            casa_apuestas=casa,
                            tipo_cuota=tipo_cuota,
                            opcion=opcion,
                            valor=cuota_valor
                        )
                    creaciones += 1

        return creaciones

    def actualizar_cuota_individual(self, cuota, dry_run=False):
        """Actualiza una cuota individual con variaciones aleatorias"""
        # Generar variación aleatoria (-10% a +10%)
        variacion = random.uniform(-0.10, 0.10)

        # Aplicar variación más conservadora para cuotas altas
        if cuota.valor > 5.0:
            variacion *= 0.5

        nuevo_valor = cuota.valor * (1 + variacion)

        # Asegurar que el valor esté dentro de rangos razonables
        nuevo_valor = max(1.01, min(100.0, nuevo_valor))

        # Redondear a 2 decimales
        nuevo_valor = round(nuevo_valor, 2)

        # Solo actualizar si cambió significativamente (> 0.01)
        if abs(nuevo_valor - cuota.valor) > 0.01:
            if not dry_run:
                cuota.valor_anterior = cuota.valor
                cuota.valor = nuevo_valor
                cuota.save()
            return True

        return False

    def obtener_opciones_por_tipo(self, tipo_cuota):
        """Retorna las opciones disponibles para cada tipo de cuota"""
        opciones_por_tipo = {
            '1x2': ['1', 'X', '2'],
            'over_under': ['Over 2.5', 'Under 2.5'],
            'handicap': ['Handicap +1', 'Handicap -1'],
            'double_chance': ['1X', '12', 'X2'],
        }

        codigo = tipo_cuota.codigo.lower()
        return opciones_por_tipo.get(codigo, [f'Opción {i}' for i in range(1, 4)])

    def generar_cuota_base(self, tipo_cuota):
        """Genera un valor base para un tipo de cuota"""
        bases_por_tipo = {
            '1x2': (1.5, 4.0),
            'over_under': (1.8, 2.2),
            'handicap': (1.7, 2.5),
            'double_chance': (1.2, 1.8),
        }

        codigo = tipo_cuota.codigo.lower()
        min_val, max_val = bases_por_tipo.get(codigo, (1.5, 3.0))

        return round(random.uniform(min_val, max_val), 2)
