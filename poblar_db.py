#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo
"""
import os
import django
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from comparador.models import CasaApuestas, Deporte, Evento, TipoCuota, Cuota


def poblar_casas_apuestas():
    """Crear casas de apuestas de ejemplo"""
    casas_data = [
        {
            'nombre': 'Bet365',
            'url': 'https://www.bet365.com',
            'logo': 'https://logos-world.net/wp-content/uploads/2020/12/Bet365-Logo.png'
        },
        {
            'nombre': 'William Hill',
            'url': 'https://www.williamhill.com',
            'logo': 'https://logos-world.net/wp-content/uploads/2020/12/William-Hill-Logo.png'
        },
        {
            'nombre': 'Pinnacle',
            'url': 'https://www.pinnacle.com',
            'logo': 'https://logos-world.net/wp-content/uploads/2020/12/Pinnacle-Logo.png'
        },
        {
            'nombre': 'Betfair',
            'url': 'https://www.betfair.com',
            'logo': 'https://logos-world.net/wp-content/uploads/2020/12/Betfair-Logo.png'
        },
        {
            'nombre': 'Bwin',
            'url': 'https://www.bwin.com',
            'logo': 'https://logos-world.net/wp-content/uploads/2020/12/Bwin-Logo.png'
        }
    ]

    for casa_data in casas_data:
        casa, created = CasaApuestas.objects.get_or_create(
            nombre=casa_data['nombre'],
            defaults=casa_data
        )
        if created:
            print(f'✓ Casa creada: {casa.nombre}')
        else:
            print(f'- Casa ya existe: {casa.nombre}')

    return CasaApuestas.objects.all()


def poblar_deportes():
    """Crear deportes de ejemplo"""
    deportes_data = [
        {'nombre': 'Fútbol', 'slug': 'futbol', 'icono': 'fas fa-futbol'},
        {'nombre': 'Baloncesto', 'slug': 'baloncesto', 'icono': 'fas fa-basketball-ball'},
        {'nombre': 'Tenis', 'slug': 'tenis', 'icono': 'fas fa-table-tennis'},
        {'nombre': 'Fútbol Americano', 'slug': 'futbol-americano', 'icono': 'fas fa-football-ball'},
        {'nombre': 'Golf', 'slug': 'golf', 'icono': 'fas fa-golf-ball'},
    ]

    for deporte_data in deportes_data:
        deporte, created = Deporte.objects.get_or_create(
            slug=deporte_data['slug'],
            defaults=deporte_data
        )
        if created:
            print(f'✓ Deporte creado: {deporte.nombre}')
        else:
            print(f'- Deporte ya existe: {deporte.nombre}')

    return Deporte.objects.all()


def poblar_tipos_cuota():
    """Crear tipos de cuota de ejemplo"""
    tipos_data = [
        {'nombre': '1X2', 'codigo': '1x2', 'descripcion': 'Resultado final del partido'},
        {'nombre': 'Over/Under', 'codigo': 'over_under', 'descripcion': 'Más o menos de una cantidad'},
        {'nombre': 'Handicap', 'codigo': 'handicap', 'descripcion': 'Ventaja o desventaja'},
        {'nombre': 'Doble Oportunidad', 'codigo': 'double_chance', 'descripcion': 'Dos resultados posibles'},
    ]

    for tipo_data in tipos_data:
        tipo, created = TipoCuota.objects.get_or_create(
            codigo=tipo_data['codigo'],
            defaults=tipo_data
        )
        if created:
            print(f'✓ Tipo de cuota creado: {tipo.nombre}')
        else:
            print(f'- Tipo ya existe: {tipo.nombre}')

    return TipoCuota.objects.all()


def poblar_eventos():
    """Crear eventos de ejemplo"""
    eventos_data = [
        # Fútbol
        {
            'deporte': 'futbol',
            'equipo_local': 'Real Madrid',
            'equipo_visitante': 'Barcelona',
            'fecha_evento': datetime.now() + timedelta(days=2, hours=20),
            'liga': 'La Liga',
            'pais': 'España'
        },
        {
            'deporte': 'futbol',
            'equipo_local': 'Manchester United',
            'equipo_visitante': 'Liverpool',
            'fecha_evento': datetime.now() + timedelta(days=3, hours=16),
            'liga': 'Premier League',
            'pais': 'Inglaterra'
        },
        {
            'deporte': 'futbol',
            'equipo_local': 'Juventus',
            'equipo_visitante': 'Inter Milan',
            'fecha_evento': datetime.now() + timedelta(days=1, hours=18),
            'liga': 'Serie A',
            'pais': 'Italia'
        },
        {
            'deporte': 'futbol',
            'equipo_local': 'PSG',
            'equipo_visitante': 'Marseille',
            'fecha_evento': datetime.now() + timedelta(days=4, hours=21),
            'liga': 'Ligue 1',
            'pais': 'Francia'
        },
        # Baloncesto
        {
            'deporte': 'baloncesto',
            'equipo_local': 'Los Angeles Lakers',
            'equipo_visitante': 'Golden State Warriors',
            'fecha_evento': datetime.now() + timedelta(days=1, hours=22),
            'liga': 'NBA',
            'pais': 'Estados Unidos'
        },
        {
            'deporte': 'baloncesto',
            'equipo_local': 'Real Madrid',
            'equipo_visitante': 'Barcelona',
            'fecha_evento': datetime.now() + timedelta(days=3, hours=19),
            'liga': 'ACB',
            'pais': 'España'
        },
        # Tenis
        {
            'deporte': 'tenis',
            'equipo_local': 'Rafael Nadal',
            'equipo_visitante': 'Roger Federer',
            'fecha_evento': datetime.now() + timedelta(days=2, hours=14),
            'liga': 'ATP',
            'pais': 'Suiza'
        },
    ]

    deportes = {d.slug: d for d in Deporte.objects.all()}

    for evento_data in eventos_data:
        deporte_slug = evento_data.pop('deporte')
        if deporte_slug in deportes:
            evento_data['deporte'] = deportes[deporte_slug]

            evento, created = Evento.objects.get_or_create(
                deporte=evento_data['deporte'],
                equipo_local=evento_data['equipo_local'],
                equipo_visitante=evento_data['equipo_visitante'],
                fecha_evento=evento_data['fecha_evento'],
                defaults=evento_data
            )
            if created:
                print(f'✓ Evento creado: {evento}')
            else:
                print(f'- Evento ya existe: {evento}')

    return Evento.objects.all()


def poblar_cuotas():
    """Crear cuotas de ejemplo para los eventos"""
    eventos = Evento.objects.all()
    casas = CasaApuestas.objects.filter(activa=True)
    tipos_cuota = TipoCuota.objects.all()

    if not eventos.exists() or not casas.exists() or not tipos_cuota.exists():
        print('⚠️ No hay eventos, casas o tipos de cuota suficientes')
        return

    cuotas_creadas = 0

    for evento in eventos:
        for tipo_cuota in tipos_cuota:
            opciones = obtener_opciones_por_tipo(tipo_cuota)

            for opcion in opciones:
                for casa in casas:
                    # Verificar si ya existe la cuota
                    if not Cuota.objects.filter(
                        evento=evento,
                        casa_apuestas=casa,
                        tipo_cuota=tipo_cuota,
                        opcion=opcion
                    ).exists():
                        # Generar cuota aleatoria
                        cuota_valor = generar_cuota_aleatoria(tipo_cuota)

                        Cuota.objects.create(
                            evento=evento,
                            casa_apuestas=casa,
                            tipo_cuota=tipo_cuota,
                            opcion=opcion,
                            valor=cuota_valor
                        )
                        cuotas_creadas += 1

    print(f'✓ {cuotas_creadas} cuotas creadas')


def obtener_opciones_por_tipo(tipo_cuota):
    """Retorna las opciones disponibles para cada tipo de cuota"""
    opciones_por_tipo = {
        '1x2': ['1', 'X', '2'],
        'over_under': ['Over 2.5', 'Under 2.5'],
        'handicap': ['Handicap +1', 'Handicap -1'],
        'double_chance': ['1X', '12', 'X2'],
    }

    codigo = tipo_cuota.codigo.lower()
    return opciones_por_tipo.get(codigo, [f'Opción {i}' for i in range(1, 4)])


def generar_cuota_aleatoria(tipo_cuota):
    """Genera un valor aleatorio para un tipo de cuota"""
    bases_por_tipo = {
        '1x2': (1.5, 4.0),
        'over_under': (1.8, 2.2),
        'handicap': (1.7, 2.5),
        'double_chance': (1.2, 1.8),
    }

    codigo = tipo_cuota.codigo.lower()
    min_val, max_val = bases_por_tipo.get(codigo, (1.5, 3.0))

    return round(random.uniform(min_val, max_val), 2)


def main():
    """Función principal"""
    print('🚀 Iniciando población de base de datos...\n')

    try:
        print('📊 Creando casas de apuestas...')
        casas = poblar_casas_apuestas()
        print(f'✓ {casas.count()} casas de apuestas\n')

        print('🏆 Creando deportes...')
        deportes = poblar_deportes()
        print(f'✓ {deportes.count()} deportes\n')

        print('🎯 Creando tipos de cuota...')
        tipos = poblar_tipos_cuota()
        print(f'✓ {tipos.count()} tipos de cuota\n')

        print('📅 Creando eventos...')
        eventos = poblar_eventos()
        print(f'✓ {eventos.count()} eventos\n')

        print('💰 Creando cuotas...')
        poblar_cuotas()

        total_cuotas = Cuota.objects.count()
        print(f'✓ {total_cuotas} cuotas totales\n')

        print('🎉 ¡Base de datos poblada exitosamente!')
        print(f'   - {casas.count()} casas de apuestas')
        print(f'   - {deportes.count()} deportes')
        print(f'   - {tipos.count()} tipos de cuota')
        print(f'   - {eventos.count()} eventos')
        print(f'   - {total_cuotas} cuotas')

    except Exception as e:
        print(f'❌ Error durante la población: {e}')
        raise


if __name__ == '__main__':
    main()
