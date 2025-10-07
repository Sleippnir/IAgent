import 'package:flutter/material.dart';
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

class AvatarInterviewPage extends StatefulWidget {
  final int interviewId;
  final String jobRole;
  final String candidateName;

  const AvatarInterviewPage({
    super.key,
    required this.interviewId,
    required this.jobRole,
    required this.candidateName,
  });

  @override
  State<AvatarInterviewPage> createState() => _AvatarInterviewPageState();
}

class _AvatarInterviewPageState extends State<AvatarInterviewPage> {
  final String viewId = 'avatar-iframe';

  @override
  void initState() {
    super.initState();
    _registerIframe();
  }

void _registerIframe() {
  // TEMPORAL: Hardcodeado para prueba
  final url = 'http://localhost:8888/index.html?interview_id=1';
  
  print('DEBUG: Cargando iframe con URL: $url');
  
  ui_web.platformViewRegistry.registerViewFactory(
    viewId,
    (int id) {
      final iframe = html.IFrameElement()
        ..src = url
        ..style.border = 'none'
        ..style.width = '100%'
        ..style.height = '100%'
        ..allow = 'camera; microphone';
      
      return iframe;
    },
  );
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Entrevista - ${widget.jobRole}'),
        backgroundColor: const Color(0xFF6ECCC4),
        foregroundColor: Colors.white,
      ),
      body: HtmlElementView(viewType: viewId),
    );
  }
}