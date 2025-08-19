import os
from django.core.management.base import BaseCommand
from documentacion.models import DocumentoMarkdown

class Command(BaseCommand):
    help = 'Limpia documentos de la base de datos que ya no tienen archivo físico'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Iniciando limpieza de documentos huérfanos...")
        
        documentos_eliminados = 0
        documentos_totales = DocumentoMarkdown.objects.count()
        
        for doc in DocumentoMarkdown.objects.all():
            if not os.path.exists(doc.archivo_markdown):
                self.stdout.write(f"❌ Eliminando documento huérfano: {doc.titulo} -> {doc.archivo_markdown}")
                doc.delete()
                documentos_eliminados += 1
            else:
                self.stdout.write(f"✅ Documento válido: {doc.titulo}")
        
        self.stdout.write("\n📊 Resumen:")
        self.stdout.write(f"   • Documentos iniciales: {documentos_totales}")
        self.stdout.write(f"   • Documentos eliminados: {documentos_eliminados}")
        self.stdout.write(f"   • Documentos restantes: {DocumentoMarkdown.objects.count()}")
        
        if documentos_eliminados > 0:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Limpieza completada! Se eliminaron {documentos_eliminados} documentos huérfanos."))
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ No se encontraron documentos huérfanos."))
